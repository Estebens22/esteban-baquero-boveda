# Kit — Robot bípedo que aprende a caminar con IA (RL sim-to-real)

Corre con **solo Python** (librería estándar, sin instalar nada):

```bash
python3 gait.py --demo      # entrena una política de equilibrio con RL (CEM) y se autoverifica
python3 gait.py             # muestra la curva de aprendizaje
python3 deploy.py --demo    # boceto del lazo sim-to-real (MOCK, sin hardware)
```

## La idea en una línea
Un robot no se programa paso a paso para caminar: **aprende** en un simulador. Una
política (red/función) propone acciones, el simulador la premia por no caerse y
avanzar, y un optimizador la mejora miles de veces. Esa política entrenada se baja
al robot real. Eso es lo que mostró **NVIDIA** con **Isaac Lab**.

## Qué hay en el kit
- **`gait.py`** — el bucle de RL de verdad, en chiquito: entrena con **CEM**
  (Cross-Entropy Method, se usa en robótica real) una política que equilibra un
  péndulo invertido. El equilibrio es el primer ladrillo de la marcha. El `--demo`
  compara contra una política al azar (≈31/500 pasos) vs la aprendida (500/500).
- **`deploy.py`** — el **puente sim-to-real**: cómo la política entrenada lee
  sensores y manda ángulos a los servos (con *clamp* de seguridad). MOCK sin hardware.
- **`firmware/walker.ino`** — controlador de patas para ESP32 (recibe ángulos por
  serial, limita cada articulación).
- **`BOM.md`** — lista de materiales (~$350–500, clase Zeroth Bot).

## El pipeline real (cuando lo armes de verdad)
1. **Modela el robot** en URDF/MJCF (medidas, masas, articulaciones).
2. **Entrena en simulación** con **MuJoCo** o **NVIDIA Isaac Lab** usando **PPO**
   (RL), con miles de robots en paralelo. Recompensa = avanzar + no caerse + suave.
3. **Domain randomization**: varía fricción, masa, retardo de los servos en el sim,
   para que la política aguante el mundo real (es la clave del sim-to-real).
4. **Exporta la política** y córrela en el robot (como `deploy.py`, pero con tus drivers).

## La parte difícil (honesto)
- **Entrenar RL pide GPU.** El robot no entrena solo; se entrena en una GPU (gaming
  o cloud) y se baja la política ya hecha.
- **El sim-to-real es el 80% del trabajo:** calibrar actuadores (SysID), el IMU y la
  fricción. Con servos baratos camina, pero tambalea.
- Este kit es **didáctico** (equilibrio en cart-pole), no entrena una marcha completa.

## De dónde partir (open-source, verificado)
- **Zeroth Bot** (K-Scale Labs) — bípedo impreso en 3D, MIT, BOM desde ~$350, pipeline
  RL completo (`ksim-gym-zbot`) y sim-to-real. docs.kscale.dev/docs/zeroth-01
- **Berkeley Humanoid Lite** — open-source, transfer **zero-shot** sim→real. lite.berkeley-humanoid.org

Crédito a esos proyectos: este kit enseña el método; ellos tienen hardware probado.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale una ⭐ en GitHub](https://github.com/Estebens22)
