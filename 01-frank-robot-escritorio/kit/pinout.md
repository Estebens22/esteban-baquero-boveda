# Planos y pinout de Frank

## Cableado (ESP32 DevKit)

```
                 ESP32
              ┌───────────┐
  Servo  ◄────┤ GPIO 13   │   señal del servo (naranja)
  Ojos   ◄────┤ GPIO 12   │   DIN del NeoPixel
  Mic    ────►┤ GPIO 34   │   salida analógica (ADC1, solo entrada)
              │           │
   5V    ─────┤ 5V    GND ├───── GND común (servo + LED + mic)
              └───────────┘
```

| Señal | Pin ESP32 | Va a |
|-------|-----------|------|
| Servo PWM | GPIO 13 | cable de señal del SG90 |
| LED DIN | GPIO 12 | DIN del NeoPixel |
| Mic OUT | GPIO 34 | salida analógica del micrófono |
| 5V | 5V / VIN | V+ del servo, del LED y del mic |
| GND | GND | masa común de todo |

> Los números de pin coinciden con `firmware/frank.ino`. Si cambias el cableado,
> cambia también las constantes `PIN_*` del `.ino`.

## Carcasa 3D

Frank es una cabeza sobre una base. Imprime dos piezas:

- **base** — aloja el ESP32, el servo y la protoboard; el eje del servo asoma arriba.
- **cabeza** — se encastra en el brazo del servo; lleva los dos ojos (NeoPixel) al frente y una rejilla para el micrófono.

Parámetros de impresión: PLA, 0.2 mm de capa, 15 % de relleno, sin soportes si imprimes la cabeza boca abajo. Tolerancia del encastre servo↔cabeza: deja ~0.3 mm de holgura.

> Este kit trae los planos y el pinout; los STL de la carcasa viven en el repo
> (carpeta del playbook). Si todavía no los encuentras, cualquier soporte de
> "cabeza + servo SG90 + base para ESP32" sirve como punto de partida — lo que
> hace a Frank, Frank, es el firmware y el cerebro, no el plástico exacto.
