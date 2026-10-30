#!/usr/bin/env python3
"""Caja de Meeseeks — el cerebro de tu ayudante de voz de una sola tarea.

Aprietas el botón, aparece el ayudante (holograma), le pides UNA cosa, la
resuelve, se despide y desaparece. Como un Meeseeks: existe para una sola
tarea; en cuanto la cumple, deja de existir. Nunca se queda dando vueltas.

Lo determinista (la máquina de estados del ciclo de vida, el límite de intentos,
prender/apagar el holograma) vive aquí en código. El criterio (entender el
pedido y resolverlo) lo pone la IA cuando hay API key, o respuestas de muestra
en modo MOCK.

Solo librería estándar de Python. Sin instalar nada.

  python3 meeseeks.py --demo                        # self-check del ciclo de vida
  python3 meeseeks.py "cuanto es 12% de 80"          # un ciclo completo por texto
  python3 meeseeks.py "resumeme esto" --serial /dev/ttyUSB0  # + maneja la caja real

El firmware (meeseeks.ino) solo entiende dos comandos de holograma:
  H1  -> enciende el holograma (el ayudante aparece)
  H0  -> lo apaga (el ayudante se va)
El QUÉ decir (voz, TTS) sale por serial para que un DFPlayer/altavoz lo hable.

Interpretación fan/educativa, no comercial.
"""
import os
import re
import sys
import json
import urllib.request

# --- Ciclo de vida (una sola tarea, siempre termina) ---
IDLE, SUMMON, LISTEN, RESOLVE, FAREWELL = "IDLE", "SUMMON", "LISTEN", "RESOLVE", "FAREWELL"
MAX_ATTEMPTS = 3   # ponytail: un Meeseeks no sufre eternamente; si no resuelve, se despide igual


def step(state, resolved=False, attempts=0):
    """Siguiente estado. Determinista y testeable.

    El Meeseeks avanza en línea recta: aparece, escucha, resuelve, se despide y
    se va. La única bifurcación es RESOLVE: reintenta hasta MAX_ATTEMPTS y,
    resuelva o no, SIEMPRE acaba despidiéndose. Nunca vuelve a escuchar en la
    misma sesión (una tarea, no un asistente que se queda).
    """
    if state == IDLE:
        return SUMMON
    if state == SUMMON:
        return LISTEN
    if state == LISTEN:
        return RESOLVE
    if state == RESOLVE:
        return FAREWELL if (resolved or attempts >= MAX_ATTEMPTS) else RESOLVE
    if state == FAREWELL:
        return IDLE
    return IDLE


def hologram(state):
    """Comando de holograma para el firmware: encendido salvo en reposo."""
    return "H0" if state == IDLE else "H1"


def lifecycle(resolver):
    """Corre el ciclo completo desde IDLE (botón apretado) y devuelve la lista de
    estados visitados. `resolver()` -> bool: si el intento resolvió la tarea."""
    path = [IDLE]
    state = IDLE
    attempts = 0
    resolved = False
    guard = 0
    while True:
        guard += 1
        assert guard < 50, "el ciclo de vida nunca debe ser infinito"
        if state == RESOLVE:
            attempts += 1
            resolved = resolver()
        nxt = step(state, resolved, attempts)
        if state == FAREWELL and nxt == IDLE:
            path.append(IDLE)
            return path
        path.append(nxt)
        state = nxt


def _mock_answer(request):
    """Sin API key: resuelve lo que se pueda con stdlib, si no, pista de muestra."""
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*de\s*(\d+(?:[.,]\d+)?)", request.lower())
    if m:
        pct = float(m.group(1).replace(",", "."))
        base = float(m.group(2).replace(",", "."))
        val = pct * base / 100
        return f"{pct:g}% de {base:g} es {val:g}.", True
    return "aquí tienes una pista para empezar; exporta OPENAI_API_KEY para que lo resuelva de verdad.", True


def resolve(request):
    """Entiende y resuelve la tarea. Con OPENAI_API_KEY la hace el modelo; si no, MOCK.
    Devuelve (respuesta, resuelto:bool)."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return _mock_answer(request)
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    prompt = ("Eres un Meeseeks: existes para resolver UNA sola tarea, de forma "
              "concreta y breve, y luego te despides. Tarea del usuario: "
              f"\"{request}\". Responde en español neutro, en pocas frases, con la "
              "solución directa. No ofrezcas seguir ayudando.")
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 200, "temperature": 0.5}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            txt = json.load(r)["choices"][0]["message"]["content"].strip()
            return (txt, True) if txt else ("", False)
    except Exception:
        return "", False   # intento fallido: el ciclo reintenta y, si se agota, se despide igual


def run(request, port=None):
    """Un ciclo de vida completo, narrado, con los comandos de holograma reales."""
    serial = open(port, "w") if port else None

    def emit(cmd):
        print(f"  [firmware] {cmd}")
        if serial:
            serial.write(cmd + "\n")

    answer = [None]
    attempts = {"n": 0}

    def resolver():
        attempts["n"] += 1
        ans, ok = resolve(request)
        if ok:
            answer[0] = ans
        return ok

    state = IDLE
    while True:
        nxt = step(state, bool(answer[0]), attempts["n"]) if state != RESOLVE else None
        if state == IDLE:
            print("· en reposo"); nxt = step(state)
        elif state == SUMMON:
            emit(hologram(state)); print('  🟣 "¡Puedo ayudarte! Pídeme UNA cosa."'); nxt = step(state)
        elif state == LISTEN:
            print(f'  👂 escuché: "{request}"'); nxt = step(state)
        elif state == RESOLVE:
            resolver()
            nxt = step(state, bool(answer[0]), attempts["n"])
        elif state == FAREWELL:
            print(f'  💬 {answer[0] or "no pude resolverlo esta vez, lo siento."}')
            print('  🟣 "¡Listo! Adiós 👋"')
            emit(hologram(IDLE))   # el ayudante se apaga al irse
            nxt = step(state)
        if state == FAREWELL and nxt == IDLE:
            print("· desapareció"); break
        state = nxt
    if serial:
        serial.close()


def demo():
    # camino feliz: aparece, escucha, resuelve y se va; termina SIEMPRE en reposo
    ok_path = lifecycle(lambda: True)
    assert ok_path[0] == IDLE and ok_path[-1] == IDLE, "debe empezar y terminar en reposo"
    assert ok_path == [IDLE, SUMMON, LISTEN, RESOLVE, FAREWELL, IDLE], f"ciclo feliz inesperado: {ok_path}"
    # una sola tarea: escucha exactamente una vez por sesión
    assert ok_path.count(LISTEN) == 1, "un Meeseeks escucha UNA tarea, no se queda de asistente"
    # si NUNCA resuelve: igual se despide y termina en reposo, sin bucle infinito
    give_up = lifecycle(lambda: False)
    assert give_up[-1] == IDLE and FAREWELL in give_up, "si se rinde, igual se despide y desaparece"
    assert give_up.count(RESOLVE) == MAX_ATTEMPTS, f"debe reintentar exactamente {MAX_ATTEMPTS} veces"
    assert give_up.count(LISTEN) == 1, "ni rindiéndose vuelve a escuchar en la misma sesión"
    # holograma: encendido mientras existe, apagado en reposo
    assert hologram(IDLE) == "H0" and hologram(SUMMON) == "H1" == hologram(RESOLVE), "holograma mal mapeado"
    # el MOCK resuelve un porcentaje de verdad
    ans, ok = _mock_answer("cuanto es 12% de 80")
    assert ok and "9.6" in ans, f"el mock debería calcular 12% de 80 = 9.6, dio: {ans}"
    print("✓ demo OK — el ayudante aparece, resuelve UNA tarea y desaparece (nunca bucle infinito)")


def main(argv):
    if not argv or argv[0] == "--demo":
        return demo()
    port = None
    if "--serial" in argv:
        i = argv.index("--serial")
        port = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    run(" ".join(argv), port)


if __name__ == "__main__":
    main(sys.argv[1:])
