#!/usr/bin/env python3
"""Equipo de agentes orquestado — ejemplo mínimo y EJECUTABLE (solo stdlib).

Sin API key corre en MODO MOCK (respuestas simuladas) para que lo pruebes al toque:
    python3 orchestrator.py "Planea el lanzamiento de mi newsletter"

Con un LLM real (API compatible con OpenAI):
    export OPENAI_API_KEY=sk-...        # y opcional OPENAI_BASE_URL / OPENAI_MODEL
    python3 orchestrator.py "..."

Idea: un orquestador parte la tarea entre agentes especializados que comparten
un 'state' y se pasan el trabajo. Lo DETERMINISTA va en código (tools); el
CRITERIO va en el modelo. Cambiá/añadí agentes y herramientas a tu gusto.
"""
import os, sys, json, urllib.request

API_KEY = os.environ.get("OPENAI_API_KEY", "")
BASE = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def llm(system, user):
    """Una llamada al modelo. En MOCK devuelve algo determinista (sin red)."""
    if not API_KEY:
        return f"[MOCK · {system.split(':')[0]}] " + user.strip().replace("\n", " ")[:120]
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"].strip()


# --- herramienta de ejemplo (determinista = código, NO modelo) ---
def tool_buscar(q):
    return [f"fuente simulada sobre '{q}' #{i}" for i in range(1, 4)]


# --- agentes: cada uno con UN rol claro ---
def investiga(state):
    state["fuentes"] = tool_buscar(state["tarea"])
    state["hallazgos"] = llm(
        "Investiga: reúnes información y citas fuentes.",
        f"Tarea: {state['tarea']}\nFuentes disponibles: {state['fuentes']}")
    return state


def analiza(state):
    state["analisis"] = llm(
        "Analiza: estructuras y extraes lo clave, sin relleno.",
        f"Hallazgos:\n{state['hallazgos']}")
    return state


def construye(state):
    state["borrador"] = llm(
        "Construye: redactas el entregable final, claro y accionable.",
        f"Análisis:\n{state['analisis']}\nTarea original: {state['tarea']}")
    return state


def valida(state):
    state["revision"] = llm(
        "Valida: revisas calidad y respondes OK/NO + por qué, según la tarea.",
        f"Entregable:\n{state['borrador']}\nTarea: {state['tarea']}")
    return state


AGENTES = [("Investiga", investiga), ("Analiza", analiza),
           ("Construye", construye), ("Valida", valida)]


def orquestar(tarea):
    state = {"tarea": tarea}
    for nombre, fn in AGENTES:
        print(f"\n── {nombre} ──")
        state = fn(state)
        print(list(state.values())[-1])
    return state


if __name__ == "__main__":
    tarea = " ".join(sys.argv[1:]) or "Resume en 5 puntos cómo empezar con agentes de IA."
    print(f"Tarea: {tarea}\nModo: {'LLM real' if API_KEY else 'MOCK (sin API key)'}")
    orquestar(tarea)
    print("\n✔ Fin. En MOCK ves el flujo; con OPENAI_API_KEY ves respuestas reales.")
