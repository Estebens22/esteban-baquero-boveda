# 11 · Caja de Meeseeks — ayudante de voz de una sola tarea
### Aprietas el botón, aparece tu ayudante, le pides UNA cosa, la resuelve y se despide

**Categoría:** Hardware + IA · **Estado:** Experimento · **Nivel:** intermedio

Una caja con un botón gigante y un holograma dentro de un cilindro. Como un
Meeseeks: existe para **una sola tarea** y, al cumplirla, deja de existir. Guía
para que **tú la construyas**: impresión 3D + un ESP32 + un Pepper's ghost + IA.
Proyecto fan, educativo, no comercial.

## Qué vas a lograr
Una caja con tres partes: la **carcasa 3D** (caja + cilindro + botón), el **holograma**
(Pepper's ghost: una lámina a 45° que refleja una pantalla o LED) y el **firmware
STT→IA→TTS de una sola tarea**. Queda claro qué es **criterio del modelo** (resolver
el pedido) y qué es **código/hardware** (el ciclo de vida y el holograma).

## La idea en una imagen
```
botón → [firmware: EVENT button] → [cerebro: meeseeks.py] → H1 (aparece) → escucha → IA resuelve → H0 (se va)
 arcade       ESP32                máquina de estados        holograma      STT        criterio      holograma
```

## Pruébalo sin comprar nada (en 10 segundos)
El cerebro es **solo librería estándar de Python**. Corre el self-check y un ciclo real:
```bash
cd kit
python3 meeseeks.py --demo                 # valida el ciclo de vida (una tarea, siempre termina)
python3 meeseeks.py "cuanto es 12% de 80"  # aparece, resuelve y desaparece
```
Para que la tarea la resuelva el modelo, exporta tu `OPENAI_API_KEY` (cualquier API
estilo OpenAI). Sin ella, respuestas de muestra (y calcula porcentajes de verdad).

## Las 2 decisiones que importan
1. **Una sola tarea, y siempre termina.** El ciclo de vida es una máquina de estados
   determinista: nunca vuelve a escuchar en la misma sesión y, resuelva o no, SIEMPRE
   se despide. El tope `MAX_ATTEMPTS` evita el bucle infinito — un Meeseeks no sufre
   para siempre. Eso lo verifica el `--demo`.
2. **El cerebro decide, el firmware obedece.** El ESP32 solo ve el botón y dos comandos
   de holograma (`H1`/`H0`). Depuras el comportamiento desde el PC sin reprogramar el chip.

## Lo que incluye el kit
- **BOM** — lista de materiales (~35–45 USD) y cómo montar el Pepper's ghost.
- **Planos y pinout** — cableado, los 3 caminos de holograma y notas de la caja 3D.
- **Firmware comentado** — `firmware/meeseeks.ino` para el ESP32 (botón + holograma).
- **Cerebro** — `meeseeks.py`, que corre sin instalar nada y trae su self-check.

## Cómo extenderlo
- **Voz real:** conecta un DFPlayer Mini + altavoz, o reproduce el TTS desde el PC —
  combínalo con el playbook **Dale voz a tu producto (STT + TTS)**.
- **Holograma más vistoso:** del anillo LED a una pantalla o a una pirámide de 4 caras.
