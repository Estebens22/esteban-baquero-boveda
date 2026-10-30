# Kit — Equipo de agentes orquestado

## Correr (modo MOCK, sin API key)
```bash
python3 orchestrator.py "Planea el lanzamiento de mi newsletter"
```
Verás el flujo Investiga → Analiza → Construye → Valida pasando el `state`.

## Correr con un LLM real
```bash
cp .env.example .env     # y poné tu OPENAI_API_KEY
export $(grep -v '^#' .env | xargs)
python3 orchestrator.py "..."
```
Compatible con cualquier API estilo OpenAI (cambiá `OPENAI_BASE_URL`/`OPENAI_MODEL`).

## Cómo extenderlo
- **Agregá un agente:** una función `def mi_agente(state): ...` y sumala a `AGENTES`.
- **Agregá una herramienta:** una función determinista (como `tool_buscar`) que el agente llama.
- **Controlá costo/latencia:** menos pasos, modelo más chico, o cortá temprano si `Valida` dice OK.
