# Kit — Caja de Meeseeks, ayudante de voz de una sola tarea

Aprietas el botón, aparece un ayudante dentro del cilindro (holograma), le pides
**UNA** cosa, la resuelve, se despide y desaparece. Como un Meeseeks: existe para
una sola tarea y, al cumplirla, deja de existir. Nunca se queda dando vueltas.

Este kit trae todo para construirla: el **cerebro** (código que corre sin instalar
nada), el **firmware**, la **lista de materiales** y los **planos/pinout**.
Interpretación fan/educativa, no comercial.

## Pruébalo sin hardware (en 10 segundos)

El cerebro es **librería estándar de Python**. Corre el self-check y un ciclo real:

```bash
python3 meeseeks.py --demo                 # valida el ciclo de vida (una sola tarea, siempre termina)
python3 meeseeks.py "cuanto es 12% de 80"  # un ciclo completo por texto
```

Verás aparecer al ayudante (`[firmware] H1`), escuchar tu pedido, resolverlo,
despedirse y apagarse (`[firmware] H0`). Esos `H1`/`H0` son los comandos reales
que recibe la caja.

Con `OPENAI_API_KEY` la tarea la resuelve el modelo; sin ella, respuestas de muestra
(y calcula porcentajes de verdad):

```bash
export OPENAI_API_KEY=sk-...               # funciona con cualquier API estilo OpenAI
python3 meeseeks.py "resumeme la idea de un Meeseeks en una frase"
```

## Conéctalo a la caja real

```bash
python3 meeseeks.py "pon un timer de 5 minutos" --serial /dev/ttyUSB0
```

El `--serial` envía `H1`/`H0` por el puerto USB al ESP32 a 115200 baudios para
encender y apagar el holograma.

## Las piezas

- `meeseeks.py` — el **cerebro**: la máquina de estados del ciclo de vida
  (aparecer → escuchar → resolver → despedirse → desaparecer) y la llamada a la IA.
  Lo determinista (el ciclo, el tope de intentos, el holograma) en código; el
  criterio (resolver la tarea) en la IA.
- `firmware/meeseeks.ino` — firmware ESP32: detecta el botón y enciende/apaga el holograma.
- `BOM.md` — qué comprar (~35–45 USD) y cómo montar el Pepper's ghost.
- `pinout.md` — cómo cablearlo, los 3 caminos de holograma y notas de la caja 3D.

## Las 2 decisiones que importan

1. **Una sola tarea, y siempre termina.** El ciclo de vida es una máquina de estados
   determinista: nunca vuelve a escuchar en la misma sesión y, resuelva o no,
   SIEMPRE se despide. El tope `MAX_ATTEMPTS` evita el bucle infinito — un Meeseeks
   no sufre para siempre.
2. **El cerebro decide, el firmware obedece.** El ESP32 solo ve el botón y dos
   comandos de holograma (`H1`/`H0`). Depuras todo el comportamiento desde el PC
   sin reprogramar el chip.

## Calibra lo físico

El mundo físico necesita perillas que el código solo no ve. Ajusta en el `.ino`:

- `DEBOUNCE_MS` — si el botón "rebota" y dispara dos veces.
- `RELANZAR_MS` — cuánto ignorar reaprietes mientras el ayudante trabaja.

Y en el holograma: el fantasma se ve mejor con el interior del cilindro en negro mate.

## Cómo extenderlo

- **Voz real:** conecta un DFPlayer Mini + altavoz, o reproduce el TTS desde el PC
  (combínalo con el playbook **Dale voz a tu producto — STT + TTS**).
- **Holograma más vistoso:** sube del anillo LED a una pantalla, o a una pirámide
  de 4 caras (ver los 3 caminos en `pinout.md`).
