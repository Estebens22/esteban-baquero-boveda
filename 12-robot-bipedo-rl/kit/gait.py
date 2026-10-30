#!/usr/bin/env python3
"""Robot bípedo que aprende con IA — kit de La Bóveda (Esteban Baquero).

El corazón de un robot que camina con IA (como los de NVIDIA) es un bucle de
*reinforcement learning*: una POLÍTICA propone acciones, el SIMULADOR la premia o
la castiga, y un optimizador la MEJORA — miles de veces. Después esa política
entrenada se baja al robot real (sim-to-real).

Este demo enseña ese bucle con **solo librería estándar** de Python: entrena una
política lineal para equilibrar un péndulo invertido (cart-pole) usando CEM
(Cross-Entropy Method, el mismo método que se usa de verdad en robótica).
Es un modelo de juguete a propósito — el equilibrio es el primer paso de la marcha.
El robot de verdad usa MuJoCo / Isaac Lab + PPO en GPU (ver README).

Uso:
  python3 gait.py --demo     # entrena y verifica que aprendió a equilibrar
  python3 gait.py            # entrena y muestra la curva de aprendizaje

ponytail: CEM sobre política lineal, física Euler. Es didáctico, no sim-to-real
real. Para el robot físico: MuJoCo/Isaac Lab + PPO + domain randomization (README).
"""
import math, random, sys

# ---- Simulador de juguete: cart-pole (equilibrar = precursor de caminar) ----
G, MC, MP, L, DT = 9.8, 1.0, 0.1, 0.5, 0.02   # gravedad, masas, media-longitud, paso


def step(s, force):
    """Un paso de física (Euler). s = (x, x_dot, theta, theta_dot)."""
    x, xd, th, thd = s
    ct, st = math.cos(th), math.sin(th)
    tot = MC + MP
    temp = (force + MP * L * thd * thd * st) / tot
    thacc = (G * st - ct * temp) / (L * (4.0 / 3.0 - MP * ct * ct / tot))
    xacc = temp - MP * L * thacc * ct / tot
    return (x + DT * xd, xd + DT * xacc, th + DT * thd, thd + DT * thacc)


def rollout(w, steps=500):
    """Corre un episodio con la política lineal w; recompensa = pasos en pie."""
    s = (0.0, 0.0, random.uniform(-0.05, 0.05), 0.0)
    r = 0
    for _ in range(steps):
        force = 10.0 if (w[0]*s[0] + w[1]*s[1] + w[2]*s[2] + w[3]*s[3]) > 0 else -10.0
        s = step(s, force)
        if abs(s[0]) > 2.4 or abs(s[2]) > 0.21:   # se cayó o se salió del riel
            break
        r += 1
    return r


def evaluate(w, episodes=5):
    return sum(rollout(w) for _ in range(episodes)) / episodes


def train(generations=18, pop=30, elite=6, verbose=False):
    """CEM: muestrea políticas, conserva las mejores, reajusta la media. Aprende."""
    mean = [0.0] * 4
    std = [1.0] * 4
    hist = []
    for g in range(generations):
        cands = [[random.gauss(mean[i], std[i]) for i in range(4)] for _ in range(pop)]
        scored = sorted(((evaluate(w), w) for w in cands), key=lambda t: t[0], reverse=True)
        top = [w for _, w in scored[:elite]]
        mean = [sum(w[i] for w in top) / elite for i in range(4)]
        std = [max(0.1, (sum((w[i]-mean[i])**2 for w in top)/elite) ** 0.5) for i in range(4)]
        pop_mean = sum(sc for sc, _ in scored) / pop   # recompensa media de la generación
        hist.append(pop_mean)
        if verbose:
            bar = "#" * int(pop_mean / 10)
            print(f"  gen {g:2d}  media={pop_mean:5.0f}/500  {bar}")
    return mean, hist


def baseline_aleatorio(n=20):
    """Cuánto equilibra una política SIN entrenar (para comparar contra lo aprendido)."""
    return sum(evaluate([random.gauss(0, 1) for _ in range(4)], episodes=3) for _ in range(n)) / n


def demo():
    """Self-check: lo entrenado debe equilibrar mucho mejor que una política al azar."""
    random.seed(7)
    base = baseline_aleatorio()
    mean, hist = train()
    final = evaluate(mean, episodes=10)
    print(f"✓ demo OK — al azar: {base:.0f}/500 · aprendido: {final:.0f}/500 "
          f"(la media subió {hist[0]:.0f}→{hist[-1]:.0f})")
    assert hist[-1] > hist[0] + 20, "la media poblacional no mejoró: el bucle de RL está roto"
    assert final >= 300, f"no aprendió a equilibrar (final={final:.0f}, esperaba >=300)"
    assert final > base * 1.5, f"no superó al azar (aprendido={final:.0f}, azar={base:.0f})"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        random.seed(7)
        print("Entrenando política de equilibrio con CEM (RL)…")
        w, hist = train(verbose=True)
        print(f"\nPolítica aprendida: {[round(x,2) for x in w]}")
        print(f"Recompensa final: {evaluate(w, episodes=10):.0f}/500 pasos en pie.")
        print("\nEste es el mismo bucle que entrena la marcha de un bípedo —")
        print("allá se cambia el cart-pole por un modelo MuJoCo/Isaac Lab del robot.")
