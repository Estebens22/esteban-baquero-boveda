#!/usr/bin/env python3
"""Puente sim-to-real (boceto) — baja una política entrenada al robot real.

La política vive como unos pocos números (pesos). En el robot, un lazo rápido lee
los sensores (IMU + encoders), evalúa la política y manda ángulos a los servos.
Esto es el boceto del lazo; en hardware reemplazas `leer_sensores` y `mover_servos`
por tus drivers (p. ej. Feetech/Dynamixel + IMU), como hace kos-zbot de Zeroth.

Uso:
  python3 deploy.py --demo    # corre el lazo en MOCK (sin hardware) y se autoverifica
"""
import sys

POLITICA = [0.1, 0.5, 8.0, 1.2]   # pesos de ejemplo (en real: los que entrenó gait.py)
SERVO_MIN, SERVO_MAX = 0, 180     # límites físicos del servo (grados)


def leer_sensores():
    # MOCK: en hardware, aquí va el IMU (ángulo/vel. del torso) + encoders de cadera.
    return (0.0, 0.0, 0.03, 0.0)


def politica(estado, w):
    u = sum(w[i] * estado[i] for i in range(4))
    return 10.0 if u > 0 else -10.0          # fuerza/torque objetivo


def a_angulo_servo(fuerza):
    # mapea el torque de la política a un ángulo de cadera, SIEMPRE dentro de límites
    ang = 90 + fuerza * 3
    return max(SERVO_MIN, min(SERVO_MAX, ang))   # clamp: nunca mandes fuera de rango


def mover_servos(angulo):
    # MOCK: en hardware, aquí va el driver del servo (bus serial Feetech/PWM).
    return angulo


def lazo(pasos=5, w=POLITICA):
    cmds = []
    for _ in range(pasos):
        s = leer_sensores()
        f = politica(s, w)
        ang = a_angulo_servo(f)
        mover_servos(ang)
        cmds.append(ang)
    return cmds


def demo():
    cmds = lazo()
    assert cmds, "el lazo no produjo comandos"
    assert all(SERVO_MIN <= a <= SERVO_MAX for a in cmds), "comando fuera de límites del servo"
    print(f"✓ demo OK — lazo sim-to-real (MOCK): {len(cmds)} comandos de servo, todos en rango {cmds}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        print(__doc__)
        print("Comandos de ejemplo:", lazo())
