# 12 · Robot bípedo que aprende a caminar con IA (RL sim-to-real)

**Estado:** Experimento · **Tema:** Hardware + IA

Cómo se construye un robot bípedo pequeño que **aprende** a caminar — igual que los que mostró NVIDIA: entrenas la marcha en un **simulador** con *reinforcement learning* y bajas esa política al robot real (**sim-to-real**). Con un demo que corre en 10 segundos y muestra el bucle de RL de verdad, sin GPU.

## Qué vas a construir
- El **bucle de RL** (política → recompensa → mejora) que aprende a equilibrar — el primer ladrillo de la marcha.
- El **puente sim-to-real**: cómo la política entrenada mueve los servos del robot real (con límites de seguridad).
- El **firmware** de las patas (ESP32 + servos) y la **lista de materiales** (~$350–500).

## Corre el ejemplo
```bash
cd kit
python3 gait.py --demo      # aprende a equilibrar con RL (CEM)
python3 deploy.py --demo    # el lazo sim-to-real en MOCK
```

## La idea
Un bípedo no se programa a mano para caminar: aprende en simulación (MuJoCo / NVIDIA Isaac Lab) con **PPO**, con miles de robots en paralelo, y la política se transfiere al hardware. La clave para que funcione en el mundo real es el **domain randomization** (variar fricción, masa y retardos en el sim).

## Honesto
- **Entrenar pide GPU** (local o cloud); el robot no entrena solo.
- El **sim-to-real** (calibrar actuadores, IMU, fricción) es el 80% del trabajo.
- Este kit es **didáctico** (equilibrio en cart-pole), no una marcha completa. Para hardware probado, parte de **Zeroth Bot** (MIT, ~$350) o **Berkeley Humanoid Lite** (transfer zero-shot sim→real).

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale una ⭐ en GitHub](https://github.com/Estebens22)
