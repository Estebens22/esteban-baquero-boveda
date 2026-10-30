# 01 · Frank — compañero de escritorio con IA
### De un modelo que solo chatea a un compañero físico que te mira, te escucha y reacciona

**Categoría:** Hardware + IA · **Estado:** En producción · **Nivel:** intermedio

Una guía para que **tú lo construyas**: impresión 3D + un microcontrolador + IA para tener a Frank sobre tu escritorio. Mira hacia tu voz, cambia el color de sus ojos según el ánimo y te habla.

## Qué vas a lograr
Un robot de escritorio con tres partes: la **carcasa 3D**, el **firmware** que lo da vida en un ESP32, y el **cerebro** con IA que decide cómo reacciona. Queda claro qué es **criterio del modelo** (la frase) y qué es **código/hardware** (hacia dónde mira, de qué color se ponen los ojos).

## La idea en una imagen
```
sonido / te llama  →  [cerebro: frank.py]  →  S<ángulo> L<color> "<frase>"  →  [firmware ESP32]
     micrófono            decide reacción          comando por serial            servo + ojos + voz
```

## Pruébalo sin comprar nada (en 10 segundos)
El cerebro es **solo librería estándar de Python**. Corre el self-check y simula eventos:
```bash
cd kit
python3 frank.py --demo                 # valida el mapeo evento -> reacción
python3 frank.py name_called            # te mira de frente, ojos atentos
python3 frank.py speech --level 0.8     # voz animada: gira y se pone alegre
```
Para que la frase la escriba el modelo, exporta tu `OPENAI_API_KEY` (funciona con cualquier API estilo OpenAI). Sin ella, Frank usa frases de muestra.

## Las 3 decisiones que importan
1. **Lo determinista en el hardware, el criterio en la IA.** Hacia dónde mira y de qué color se pone lo calcula el código; qué dice lo pone el modelo. Si la IA falla, Frank igual hace su gesto — no se queda roto.
2. **El cerebro vive en tu PC, el firmware solo ejecuta.** El ESP32 no "piensa": lee el micrófono, avisa y obedece comandos `S<ángulo> L<color> "<frase>"`. Así depuras el comportamiento sin reprogramar el chip.
3. **Calibra el mundo físico.** Un servo queda torcido y un micrófono lee distinto en cada cuarto. El kit deja las perillas (`SERVO_TRIM`, `MIC_BASELINE`, `MIC_TRIGGER`) a la vista.

## Lo que incluye el kit
- **BOM** — lista de materiales (~25–30 USD).
- **Planos y pinout** — cómo cablearlo y notas de la carcasa 3D.
- **Firmware comentado** — `firmware/frank.ino` para el ESP32.
- **Cerebro** — `frank.py`, que corre sin instalar nada y trae su self-check.

## Cómo extenderlo
- **Nuevo gesto:** agrega un evento en `plan()` (p. ej. "despedida" → gira y ojos cálidos).
- **Voz real:** conecta un DFPlayer Mini + altavoz donde el firmware hoy imprime la frase.
- **Más sentidos:** suma un sensor (distancia, luz) que genere nuevos eventos para el cerebro.

## Descargas
Kit en `kit/` (frank.py, firmware, BOM, pinout, README) y el **ZIP** con todo. Combínalo con el **08 · Dale voz a tu producto** para que Frank hable y escuche de verdad.

---
Hecho por **Esteban Baquero** · [estebanbaquero.com](https://estebanbaquero.com) · De una idea a un sistema que funciona.
Si te sirve, **sígueme y dale ⭐** → [github.com/Estebens22](https://github.com/Estebens22)
