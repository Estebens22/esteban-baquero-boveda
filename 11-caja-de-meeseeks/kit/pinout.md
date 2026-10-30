# Planos y pinout de la Caja de Meeseeks

## Cableado (ESP32 DevKit)

```
                 ESP32
              ┌───────────┐
  Botón  ────►┤ GPIO 27   │   a GND (pull-up interno; apretado = LOW)
  Hologr.◄────┤ GPIO 14   │   a la compuerta del MOSFET / IN del relé
              │           │
   5V    ─────┤ 5V    GND ├───── GND común (botón, MOSFET, luz, mic)
              └───────────┘
```

| Señal | Pin ESP32 | Va a |
|-------|-----------|------|
| Botón | GPIO 27 | un contacto del botón; el otro a GND |
| Holograma | GPIO 14 | gate del MOSFET (o IN del relé) que enciende la luz/pantalla |
| 5V | 5V / VIN | alimentación de la luz del holograma (por el MOSFET) y periféricos |
| GND | GND | masa común de todo (incluida la fuente de la luz) |

> Los números de pin coinciden con `firmware/meeseeks.ino`. Si cambias el
> cableado, cambia también las constantes `PIN_*` del `.ino`.

## El holograma (Pepper's ghost)

```
        cilindro transparente
            ╱│
   LED/    ╱ │   ← lámina a 45° refleja hacia el ojo del observador
  pantalla  ╲│
   (abajo)   ▀  ← la imagen "flota" dentro del cilindro
```

Una lámina transparente a 45° sobre una fuente de imagen (pantalla o tira LED)
crea el reflejo "flotante". Cuanto más oscuro el fondo del cilindro, más nítido
el fantasma. Enciende/apaga esa fuente con el pin del holograma (`H1`/`H0`).

**Los 3 caminos de holograma** (de más fácil a más vistoso):
1. **Tira/anillo LED** — barato; el ayudante es una silueta/pulso de color. Lo que trae la BOM por defecto.
2. **Pantalla pequeña** (OLED/TFT o un móvil viejo) reproduciendo un loop del personaje. Más "cara".
3. **Pirámide de 4 caras** de acrílico sobre la pantalla — holograma visible desde varios ángulos.

## La caja 3D

Tres piezas en PLA:

- **base** — aloja el ESP32, el MOSFET/relé y la protoboard.
- **cilindro + soporte de la lámina a 45°** — la "cámara" del holograma; fondo oscuro mate por dentro.
- **tapa del botón** — rebaja para encastrar el botón arcade de 60 mm arriba.

Parámetros de impresión: PLA, 0.2 mm de capa, 15 % de relleno. El cilindro, mejor
en material translúcido o con una ventana; el interior píntalo de negro mate para
que el fantasma resalte.

> Este kit trae los planos y el pinout; los STL exactos de la caja viven en el
> repo del playbook. Si aún no los encuentras, cualquier soporte de "Pepper's
> ghost + base para ESP32 + botón arcade" sirve de punto de partida — lo que hace
> a la caja un Meeseeks es el firmware y el cerebro de una sola tarea, no el
> plástico exacto.
