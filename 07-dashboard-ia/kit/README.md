# Kit — Dashboard que decide con IA

Corre con **solo Python** (librería estándar, sin instalar nada).

```bash
python3 dashboard.py --demo     # self-check de los KPIs y las señales
python3 dashboard.py            # imprime KPIs + decisión y genera dashboard.html
```

Abre el `dashboard.html` que se genera: vas a ver las tarjetas de KPIs, las
señales detectadas y la **decisión** (qué hacer esta semana).

- `data/ventas.csv` — tus datos (`fecha, ingresos, pedidos, gasto_ads`). Reemplaza la muestra por los tuyos.
- `prompts/analisis.md` — el prompt que convierte los números en una decisión.
- Sin `OPENAI_API_KEY` → modo **MOCK**: decide por reglas, transparente, sin inventar.
- Con `OPENAI_API_KEY` → el modelo interpreta los KPIs y redacta la decisión:

```bash
export OPENAI_API_KEY=sk-...    # funciona con cualquier API estilo OpenAI
# opcional: OPENAI_BASE_URL, OPENAI_MODEL
python3 dashboard.py
```

## Cómo funciona (3 piezas)
1. **Carga** — lee `data/ventas.csv`.
2. **KPIs** — el código calcula las cifras exactas (ingresos, ticket, ROAS, semana vs semana) y detecta **señales**.
3. **Decisión** — el modelo (o las reglas) interpreta esas señales y propone **una sola acción** medible.

La clave: el **código hace la aritmética**, el **modelo pone el criterio**. Le pasas las cifras ya calculadas, no la tabla cruda — así no alucina números.

El límite honesto: KPIs en memoria sobre un CSV. Para una fuente viva (base de datos o API) o millones de filas, solo cambias la pieza de **Carga** por una query; KPIs y Decisión quedan igual.
