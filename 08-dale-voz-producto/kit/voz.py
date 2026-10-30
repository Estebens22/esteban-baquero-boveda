#!/usr/bin/env python3
"""Dale voz a tu producto — STT + TTS — kit de La Bóveda (Esteban Baquero).

Que tu producto ESCUCHE y HABLE, sin depender de una caja negra:

  audio → [STT: habla→texto] → [lógica] → respuesta → [TTS: texto→habla] → audio

Tres piezas, cada una con un MOCK de solo-stdlib (corre sin instalar ni pagar nada)
y un modo REAL por API (mismo contrato, lo enchufas cuando quieras):

  1. STT   — reconocimiento de voz (habla → texto)
  2. TTS   — síntesis de voz (texto → habla), con una COMPUERTA de consentimiento
  3. FLUJO — el ciclo de conversación que une las dos

El mock de TTS escribe un .wav REAL y reproducible (un tono por palabra) con el
módulo `wave` de la librería estándar; el mock de STT lee el texto del lado del
.wav. No es un modelo acústico: es el andamio honesto para que el pipeline corra
de punta a punta sin red. El modo REAL (Whisper / API de TTS) hace la
transcripción y la síntesis de verdad, detrás de la MISMA interfaz.

Uso:
  python3 voz.py --demo                        # self-check: round-trip STT↔TTS + compuerta
  python3 voz.py "hola, ¿qué puedes hacer?"    # corre el flujo de conversación (mock)
  OPENAI_API_KEY=... python3 voz.py "..."      # usa STT/TTS reales por API

ponytail: TTS de andamio por tonos; migrar a Piper/Coqui/ElevenLabs es cambiar
`sintetizar_real`. El contrato (texto→wav) y la compuerta de consentimiento no cambian.
"""
import os, sys, json, math, wave, struct, urllib.request

SR = 16000  # sample rate del WAV mock (16 kHz mono, lo que piden los STT)

# Voces genéricas sintéticas, sin dueño: no exigen consentimiento.
VOCES_SEGURAS = {"neutral"}


# ---------- utilidades de audio (solo stdlib) ----------
def _tono(freq, dur, vol=0.3):
    """Genera frames PCM 16-bit de un tono (freq=0 → silencio)."""
    for i in range(int(SR * dur)):
        muestra = vol * math.sin(2 * math.pi * freq * i / SR) if freq else 0.0
        yield struct.pack("<h", int(muestra * 32767))


# ---------- 1. STT (habla → texto) ----------
def transcribir_mock(ruta):
    """Stand-in de stdlib: recupera el texto del .txt que deja el TTS mock.
    No es un modelo acústico; el modo real transcribe audio de verdad."""
    lado = ruta + ".txt"
    if not os.path.exists(lado):
        raise ValueError(
            f"el STT mock no puede transcribir {ruta} sin su '{os.path.basename(lado)}' "
            "(no es un modelo acústico — usa OPENAI_API_KEY para STT real)")
    with open(lado, encoding="utf-8") as f:
        return f.read().strip()


def transcribir_real(ruta):
    """Whisper (o API compatible): audio → texto, de verdad. multipart con stdlib."""
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_STT_MODEL", "whisper-1")
    bound = "----vozkit" + str(os.getpid())
    with open(ruta, "rb") as f:
        audio = f.read()
    body = b"".join([
        f"--{bound}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{model}\r\n".encode(),
        f"--{bound}\r\nContent-Disposition: form-data; name=\"file\"; "
        f"filename=\"audio.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode(),
        audio,
        f"\r\n--{bound}--\r\n".encode(),
    ])
    req = urllib.request.Request(
        f"{base}/audio/transcriptions", data=body,
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": f"multipart/form-data; boundary={bound}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["text"].strip()


def transcribir(ruta):
    return transcribir_real(ruta) if os.environ.get("OPENAI_API_KEY") else transcribir_mock(ruta)


# ---------- 2. TTS (texto → habla) con compuerta de consentimiento ----------
def sintetizar_mock(texto, ruta):
    """Escribe un .wav REAL (un tono por palabra) + un .txt lado para el STT mock."""
    palabras = texto.split() or ["."]
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for p in palabras:
            freq = 180 + (len(p) * 37) % 300  # 180–480 Hz, determinista por palabra
            for b in _tono(freq, 0.18):
                w.writeframes(b)
            for b in _tono(0, 0.06):          # silencio entre palabras
                w.writeframes(b)
    with open(ruta + ".txt", "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta


def sintetizar_real(texto, ruta, voz):
    """API de TTS: texto → WAV, de verdad."""
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    body = json.dumps({
        "model": model,
        "voice": "alloy" if voz == "neutral" else voz,
        "input": texto,
        "response_format": "wav",
    }).encode()
    req = urllib.request.Request(
        f"{base}/audio/speech", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r, open(ruta, "wb") as f:
        f.write(r.read())
    return ruta


def sintetizar(texto, ruta, voz="neutral", consentimiento=False):
    """Síntesis con COMPUERTA de voz responsable.

    Usar la voz de una persona real (clonada o identificable) exige
    consentimiento explícito. Las voces genéricas ('neutral') no lo requieren.
    """
    if voz not in VOCES_SEGURAS and not consentimiento:
        raise PermissionError(
            f"voz '{voz}' no es genérica: clonar o usar una voz identificable exige "
            "consentimiento explícito (consentimiento=True). Ver VOZ-RESPONSABLE.md")
    if os.environ.get("OPENAI_API_KEY"):
        return sintetizar_real(texto, ruta, voz)
    return sintetizar_mock(texto, ruta)


# ---------- 3. FLUJO de conversación ----------
def responder(texto):
    """Lógica mínima de conversación (regla simple, determinista).
    Aquí enchufas tu LLM/agente; el flujo de voz no cambia."""
    t = texto.lower()
    if any(s in t for s in ("hola", "buenas", "buenos días", "buenas tardes")):
        return "¡Hola! Puedo escucharte y responderte con voz. ¿En qué te ayudo?"
    if "qué puedes" in t or "que puedes" in t or "ayuda" in t:
        return "Convierto tu voz en texto, pienso una respuesta y te la devuelvo hablada."
    if any(s in t for s in ("adiós", "adios", "chao", "gracias")):
        return "¡Listo! Que te vaya bien."
    return f"Entendí: {texto}. Cuéntame más y te ayudo."


def conversar(audio_in=None, texto_in=None, ruta_out="respuesta.wav"):
    """Un turno completo: audio/texto → STT → lógica → TTS → audio.
    Devuelve (lo_que_escuché, lo_que_respondo, ruta_wav)."""
    if audio_in:
        escuchado = transcribir(audio_in)
    elif texto_in is not None:
        escuchado = texto_in
    else:
        raise ValueError("pasa audio_in o texto_in")
    respuesta = responder(escuchado)
    sintetizar(respuesta, ruta_out, voz="neutral")
    return escuchado, respuesta, ruta_out


# ---------- self-check ----------
def demo():
    """Corre 100% offline (mock): WAV válido, round-trip exacto, compuerta y flujo."""
    import tempfile
    key = os.environ.pop("OPENAI_API_KEY", None)  # forzar mock durante la demo
    try:
        d = tempfile.mkdtemp()

        # 1. el TTS mock produce un WAV válido y no vacío
        w = sintetizar("hola mundo esto es voz", os.path.join(d, "a.wav"))
        with wave.open(w) as f:
            assert f.getnframes() > 0 and f.getframerate() == SR and f.getnchannels() == 1

        # 2. round-trip STT↔TTS: lo que sintetizo, lo transcribo IGUAL
        texto = "una prueba de ida y vuelta"
        r = os.path.join(d, "rt.wav")
        sintetizar(texto, r)
        assert transcribir_mock(r) == texto, "el round-trip STT↔TTS no coincide"

        # 3. compuerta: voz identificable SIN consentimiento = bloqueada; CON = pasa
        try:
            sintetizar("x", os.path.join(d, "x.wav"), voz="esteban_real")
            raise AssertionError("debió exigir consentimiento")
        except PermissionError:
            pass
        sintetizar("ok", os.path.join(d, "y.wav"), voz="esteban_real", consentimiento=True)

        # 4. flujo completo de conversación
        esc, resp, ruta = conversar(texto_in="hola, ¿qué puedes hacer?",
                                    ruta_out=os.path.join(d, "c.wav"))
        assert esc and resp and os.path.exists(ruta)
        with wave.open(ruta) as f:
            assert f.getnframes() > 0

        print("✓ demo OK — WAV válido, round-trip STT↔TTS exacto, "
              "compuerta de consentimiento activa, flujo de conversación corre")
    finally:
        if key is not None:
            os.environ["OPENAI_API_KEY"] = key


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        texto = " ".join(sys.argv[1:]) or "hola, ¿qué puedes hacer?"
        modo = "REAL (API)" if os.environ.get("OPENAI_API_KEY") else "MOCK (stdlib)"
        esc, resp, ruta = conversar(texto_in=texto)
        print(f"Modo: {modo}\n")
        print(f"🗣️  escuché:  {esc}")
        print(f"🤖 respondo: {resp}")
        print(f"🔊 audio:    {ruta}   (reprodúcelo: afplay {ruta}  /  aplay {ruta})")
