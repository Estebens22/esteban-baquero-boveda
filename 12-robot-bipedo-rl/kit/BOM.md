# Lista de materiales (BOM) — robot bípedo que aprende con IA

Rango de referencia para un bípedo pequeño impreso en 3D (clase Zeroth Bot, ~$350–500 USD).
Es una propuesta reproducible; confirma modelos, voltajes y par (torque) antes de comprar.

## Cómputo y sensores
| Pieza | Para qué | Notas | Cant. |
|---|---|---|---|
| Raspberry Pi 5 (o Jetson Orin Nano) | Cerebro: corre la política + visión | Jetson si quieres visión pesada | 1 |
| microSD 64 GB + fuente | SO y arranque | — | 1 |
| IMU 6/9 ejes (MPU-6050 / BNO055) | Equilibrio: ángulo y velocidad del torso | BNO055 trae fusión interna, más fácil | 1 |

## Actuadores (lo más importante)
| Pieza | Para qué | Notas | Cant. |
|---|---|---|---|
| Servos de bus con encoder (Feetech STS3215 o Dynamixel) | Articulaciones: cadera, rodilla, tobillo | Con realimentación de posición = sim-to-real serio | 6–8 |
| Controladora de servos / bus serial | Hablar con todos los servos | Según marca del servo | 1 |
| Fuente de poder para servos (5–8 V, ≥5 A) | Energía SOLO de los servos | **Separada** del cómputo; GND común | 1 |

## Estructura
| Pieza | Para qué | Notas | Cant. |
|---|---|---|---|
| Filamento 3D (PLA+/PETG) | Chasis, patas, pies | PETG aguanta más | — |
| Tornillería M2/M3 + rodamientos | Uniones | Kit surtido | — |
| Batería LiPo + regulador | Autonomía | Con protección | 1 |

## Para entrenar (no va en el robot)
| Recurso | Para qué | Notas |
|---|---|---|
| GPU (local gaming o cloud) | Entrenar la política RL en simulación | El robot NO entrena solo; la GPU sí |
| MuJoCo / NVIDIA Isaac Lab | Simulador físico + RL en paralelo | Gratis / open-source |

> Honestidad: es una BOM de referencia basada en builds open-source (Zeroth Bot, Berkeley Humanoid Lite). **No está validada en tu banco**: confirma par del servo contra el peso del robot, voltajes y pines antes de energizar.
