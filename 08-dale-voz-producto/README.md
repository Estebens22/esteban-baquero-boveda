# 08 · Dale voz a tu producto (STT + TTS)

**Estado:** Experimento · **Tema:** Fine-tuning

Que tu producto **escuche y hable**, sin depender de una caja negra: reconocimiento de voz (STT) + síntesis (TTS) + el flujo de conversación que los une — con **voz responsable**. Corre en 10 segundos con solo Python, sin instalar nada.

## Qué vas a construir
- **El reconocimiento (STT)** — habla → texto, detrás de una interfaz que no cambia entre mock y modelo real.
- **La síntesis (TTS)** — texto → audio, con una **compuerta de consentimiento**: usar una voz identificable exige permiso explícito.
- **El flujo de conversación** — audio → STT → lógica (aquí enchufas tu LLM) → TTS → audio, en un turno.

## Corre el ejemplo
```bash
cd kit
python3 voz.py --demo
python3 voz.py "hola, ¿qué puedes hacer?"
```

## La idea en una línea
La voz es una interfaz, no magia: un pipeline `habla→texto→lógica→texto→habla` que puedes correr, medir y cambiar pieza por pieza.

## Los errores clásicos (honesto)
- **Clonar una voz sin consentimiento** → la compuerta de `sintetizar()` lo bloquea por defecto (ver `kit/VOZ-RESPONSABLE.md`).
- **Casar el sistema con un proveedor** → STT y TTS viven detrás de una interfaz; cambiar de Whisper a Piper, o de OpenAI a ElevenLabs, no toca tu flujo.
- **No etiquetar lo sintético** → si el usuario puede confundirlo con una persona real, avísale.

## El límite honesto
El mock no transcribe audio de verdad (no hay modelo acústico en la librería estándar): escribe un WAV de tonos y recupera el texto del lado. Es el andamio para que el pipeline corra sin red. Enciende `OPENAI_API_KEY` o conecta Whisper local y el **mismo** flujo se vuelve voz real.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
