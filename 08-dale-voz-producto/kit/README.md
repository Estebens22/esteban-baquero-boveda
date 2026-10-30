# Kit — Dale voz a tu producto (STT + TTS)

Corre con **solo Python** (librería estándar, sin instalar nada).

```bash
python3 voz.py --demo                       # self-check: round-trip STT↔TTS + compuerta
python3 voz.py "hola, ¿qué puedes hacer?"   # corre el flujo de conversación (mock)
```

- `voz.py` — las 3 piezas: **STT** (habla→texto), **TTS** (texto→habla, con compuerta de consentimiento) y el **flujo** de conversación que las une.
- `VOZ-RESPONSABLE.md` — guía corta de voz responsable (consentimiento, etiquetado, privacidad).

Sin `OPENAI_API_KEY` → modo **MOCK** (solo stdlib): el TTS escribe un `.wav` real (un tono por palabra) y el STT recupera el texto del lado del `.wav`. Es el andamio honesto para que el pipeline corra de punta a punta, sin red. No es un modelo acústico.

Con `OPENAI_API_KEY` → STT y TTS **reales**, detrás de la **misma** interfaz:

```bash
export OPENAI_API_KEY=sk-...    # funciona con cualquier API estilo OpenAI
# opcional: OPENAI_BASE_URL, OPENAI_STT_MODEL (def. whisper-1), OPENAI_TTS_MODEL
python3 voz.py "léeme esto en voz alta"
```

## Las 3 piezas
1. **STT** — `transcribir(wav)` devuelve texto. Mock = lee el `.txt` lado; real = Whisper vía API.
2. **TTS** — `sintetizar(texto, ruta, voz, consentimiento)` escribe un WAV. La **compuerta** bloquea usar una voz identificable sin `consentimiento=True`.
3. **Flujo** — `conversar(texto_in=...)` hace un turno completo: STT → `responder()` (aquí enchufas tu LLM/agente) → TTS. Devuelve `(escuché, respondo, ruta_wav)`.

## Comparativa de opciones (para elegir el modo real)

| Pieza | Local / open-source | API gestionada |
|------|---------------------|----------------|
| **STT** | `whisper.cpp`, `faster-whisper` (gratis, privado, corre en tu máquina) | Whisper API, Deepgram (sin GPU, pagas por minuto) |
| **TTS** | Piper, Coqui XTTS (gratis, offline, clonación bajo tu control) | OpenAI TTS, ElevenLabs (calidad alta, pagas por carácter) |

Regla práctica: **local** cuando la privacidad o el costo por volumen mandan; **API** cuando quieres máxima calidad y cero infraestructura. Cambiar de uno a otro es cambiar `transcribir_real` / `sintetizar_real` — el contrato (texto↔wav) y la compuerta no se tocan.

El límite honesto: el mock no transcribe audio de verdad (no hay modelo acústico en la stdlib). Enciende `OPENAI_API_KEY` o conecta Whisper local y el mismo flujo se vuelve voz real.
