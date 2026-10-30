# Kit — Frank, compañero de escritorio con IA

Frank es hardware + IA: una cabeza que te mira, reacciona a tu voz y te habla.
Este kit trae todo para construirlo: el **cerebro** (código que corre sin instalar
nada), el **firmware**, la **lista de materiales** y los **planos/pinout**.

## Pruébalo sin hardware (en 10 segundos)

El cerebro de Frank es Python de **librería estándar**. Corre el self-check:

```bash
python3 frank.py --demo                  # valida el mapeo evento -> reacción
python3 frank.py name_called             # "te mira de frente"
python3 frank.py speech --level 0.8      # reacciona a voz animada
python3 frank.py idle                    # vuelve al reposo
```

Cada evento imprime el comando que recibiría Frank real:
`S<ángulo> L<rrggbb> "<frase>"` (cabeza, color de ojos, frase).

Con `OPENAI_API_KEY` la frase la escribe el modelo; sin ella, frases de muestra:

```bash
export OPENAI_API_KEY=sk-...             # funciona con cualquier API estilo OpenAI
python3 frank.py name_called
```

## Conéctalo a Frank real

```bash
python3 frank.py speech --level 0.6 --serial /dev/ttyUSB0
```

El `--serial` envía el comando por el puerto USB al ESP32 a 115200 baudios.

## Las piezas

- `frank.py` — el **cerebro**: evento sentido → ángulo de cabeza + ánimo (color) + frase.
  Lo determinista (ángulos, color) en código; el criterio (la frase) en la IA.
- `firmware/frank.ino` — firmware ESP32: lee el micrófono, mueve el servo, pinta los
  ojos y ejecuta los comandos del cerebro. Comentado línea a línea.
- `BOM.md` — qué comprar (~25–30 USD).
- `pinout.md` — cómo cablearlo y notas de la carcasa 3D.

## Calibra lo físico

Un servo real queda torcido, un micrófono lee distinto según el cuarto. Ajusta:

- `SERVO_CENTER` / `SERVO_TRIM` — si Frank no mira derecho.
- `MIC_SILENCE` (en `frank.py`) y `MIC_BASELINE` / `MIC_TRIGGER` (en el `.ino`) —
  según tu micrófono y tu ambiente.

El mundo físico necesita esa perilla; el código solo no la ve.
