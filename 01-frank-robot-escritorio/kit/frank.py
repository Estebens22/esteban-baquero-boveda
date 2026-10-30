#!/usr/bin/env python3
"""Frank — el cerebro de tu compañero de escritorio.

Mapea lo que Frank "siente" (nivel de sonido, si lo llamaste, inactividad) a una
reacción física: hacia dónde mira la cabeza (servo), de qué color se ponen los
ojos (LED) y qué dice. Lo determinista (ángulos, color por ánimo) vive aquí en
código; el criterio (la frase) lo pone la IA cuando hay API key, o frases de
muestra en modo MOCK.

Solo librería estándar de Python. Sin instalar nada.

  python3 frank.py --demo                 # self-check del mapeo de reacciones
  python3 frank.py name_called            # imprime el comando de firmware
  python3 frank.py speech --level 0.8     # reacciona a voz fuerte
  python3 frank.py idle --serial /dev/ttyUSB0   # además lo envía a Frank real

El comando de firmware que sale por serial es una línea compacta:
  S<angulo> L<rrggbb> "<frase>"
que el .ino de la carpeta firmware/ sabe interpretar.
"""
import os
import sys
import json
import urllib.request

# --- Calibración (ajústala a TU Frank; el mundo físico no es el ideal del papel) ---
SERVO_CENTER = 90      # ponytail: trim del servo de la cabeza; cámbialo si Frank mira torcido
SERVO_LEFT = 45
SERVO_RIGHT = 135
MIC_SILENCE = 0.15     # por debajo de esto = silencio (depende de tu micrófono)

# Ánimo -> color de ojos (rrggbb). El código decide el ánimo; el modelo, la frase.
MOODS = {
    "atento":  "00ff88",   # te está mirando
    "calmo":   "1133aa",   # en reposo
    "alegre":  "ffcc00",   # voz animada
    "pensando":"aa00ff",   # procesando
}


def plan(event, level=0.0):
    """Evento sentido -> (angulo_servo, ánimo). Determinista y testeable."""
    if event == "name_called":
        return SERVO_CENTER, "atento"      # te mira de frente
    if event == "speech":
        if level < MIC_SILENCE:
            return SERVO_CENTER, "calmo"
        mood = "alegre" if level >= 0.6 else "atento"
        # mira hacia la voz: más fuerte -> gira más (hacia la derecha por convención)
        angle = SERVO_CENTER + int((level - MIC_SILENCE) * (SERVO_RIGHT - SERVO_CENTER) / (1 - MIC_SILENCE))
        return min(angle, SERVO_RIGHT), mood
    if event == "idle":
        return SERVO_CENTER, "calmo"        # vuelve al reposo
    return SERVO_CENTER, "calmo"


def say(event, level, mood):
    """La frase. Con OPENAI_API_KEY la genera el modelo; si no, MOCK."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        canned = {
            "name_called": "¿me llamaste? aquí estoy.",
            "idle": "...",
            "speech": "te escucho" if mood != "alegre" else "¡me encanta esa energía!",
        }
        return canned.get(event, "...")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (f"Eres Frank, un robot de escritorio simpático y breve. "
              f"Evento: {event}, ánimo: {mood}. Responde en una sola frase corta, en español neutro.")
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 40, "temperature": 0.8}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except Exception:
        return "..."  # si falla la IA, Frank no se queda mudo-roto: sigue su gesto


def command(event, level=0.0):
    angle, mood = plan(event, level)
    phrase = say(event, level, mood).replace('"', "'")
    return f'S{angle} L{MOODS[mood]} "{phrase}"', mood


def demo():
    # name_called -> mira de frente y atento
    _, m = command("name_called")
    a, _ = plan("name_called")
    assert m == "atento" and a == SERVO_CENTER, "al llamarlo debe mirar de frente y atento"
    # idle -> vuelve al reposo, calmo
    a, m = plan("idle")
    assert a == SERVO_CENTER and m == "calmo", "inactivo debe volver al reposo"
    # voz más fuerte -> gira más (monótono) y nunca pasa el tope
    a_low, _ = plan("speech", 0.3)
    a_hi, _ = plan("speech", 0.9)
    assert SERVO_CENTER <= a_low <= a_hi <= SERVO_RIGHT, "el giro debe crecer con el volumen y no pasarse"
    # voz animada -> alegre
    _, mh = plan("speech", 0.8)
    assert mh == "alegre", "voz fuerte debe ponerlo alegre"
    # el comando sale bien formado
    cmd, _ = command("name_called")
    assert cmd.startswith("S") and ' L' in cmd and cmd.count('"') == 2, f"comando mal formado: {cmd}"
    print(f"✓ demo OK — ejemplo: {command('speech', 0.8)[0]}")


def main(argv):
    if not argv or argv[0] == "--demo":
        return demo()
    event = argv[0]
    level = 0.0
    port = None
    i = 1
    while i < len(argv):
        if argv[i] == "--level":
            level = float(argv[i + 1]); i += 2
        elif argv[i] == "--serial":
            port = argv[i + 1]; i += 2
        else:
            i += 1
    cmd, mood = command(event, level)
    print(f"[{mood}] {cmd}")
    if port:
        # stdlib: el puerto serial es un archivo. 115200 por defecto en el .ino.
        with open(port, "w") as s:
            s.write(cmd + "\n")
        print(f"→ enviado a Frank en {port}")


if __name__ == "__main__":
    main(sys.argv[1:])
