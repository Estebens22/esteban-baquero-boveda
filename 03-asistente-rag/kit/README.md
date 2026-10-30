# Kit — Asistente RAG sobre tus documentos

Corre con **solo Python** (librería estándar, sin instalar nada).

```bash
python3 rag.py --demo                       # self-check de la recuperación
python3 rag.py "¿cuál es la política de devoluciones?"
```

- `docs/` — tus documentos (`.md` o `.txt`). Reemplaza los de muestra por los tuyos.
- Sin `OPENAI_API_KEY` → modo **MOCK**: responde extractivo mostrando los trozos y de qué archivo salieron.
- Con `OPENAI_API_KEY` → el modelo redacta la respuesta **citando** las fuentes recuperadas:

```bash
export OPENAI_API_KEY=sk-...      # funciona con cualquier API estilo OpenAI
# opcional: OPENAI_BASE_URL, OPENAI_MODEL
python3 rag.py "¿hacen envíos a todo el país?"
```

## Cómo funciona (3 piezas)
1. **Ingesta** — trocea `docs/` en chunks con solape.
2. **Recuperación** — TF-IDF + coseno trae los chunks más parecidos a tu pregunta (pliega acentos).
3. **Respuesta** — el modelo responde **solo con esa evidencia** y cita `[archivo#n]`.

El límite honesto: TF-IDF alcanza para cientos/miles de chunks. Para más volumen, se pasa a embeddings + un índice vectorial — mismo flujo, otra caja de recuperación.
