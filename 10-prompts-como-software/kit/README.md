# Kit — Prompts que se comportan como software

Corre con **solo Python** (librería estándar, sin instalar nada).

```bash
python3 promptkit.py --demo     # self-check: valida el contrato y corre los evals
python3 promptkit.py            # corre los evals en modo MOCK e imprime el reporte
```

- `promptkit.py` — las 3 piezas: **esquema** (el contrato de salida), el **modelo** (mock por reglas / LLM real) y los **evals** con su reporte.
- `data/evals.json` — el set de casos (`texto` + `esperado`). Agrega los tuyos, sobre todo los ambiguos.
- Sin `OPENAI_API_KEY` → modo **MOCK**: un clasificador por reglas, determinista, hace de stand-in del modelo.
- Con `OPENAI_API_KEY` → el modelo real responde JSON y pasa por el **mismo** `validar()`:

```bash
export OPENAI_API_KEY=sk-...    # funciona con cualquier API estilo OpenAI
# opcional: OPENAI_BASE_URL, OPENAI_MODEL
python3 promptkit.py
```

## Cómo funciona (3 piezas)
1. **Esquema** — `validar()` exige el contrato (enums + tipos). Si el modelo se sale, lanza error con la razón. Nada entra al sistema sin pasar por ahí.
2. **Evals** — cada caso tiene su salida esperada. Un caso pasa si la salida es válida Y todos los campos coinciden.
3. **Ciclo** — el reporte marca cada ✗ con el campo que falló. Ajustas el prompt (o las reglas), vuelves a correr y ves el accuracy subir.

La clave: el modelo propone, el **esquema dispone**. Validas y mides — así un prompt deja de ser magia y se vuelve software que mejoras con método.

El límite honesto: un esquema pequeño y plano. Para salidas con más campos o anidadas, el `ESQUEMA` crece (o usas `jsonschema`/`pydantic`); los evals y el ciclo quedan igual.
