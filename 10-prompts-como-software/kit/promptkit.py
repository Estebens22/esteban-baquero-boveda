#!/usr/bin/env python3
"""Prompts que se comportan como software — kit de La Bóveda (Esteban Baquero).

Un prompt sin evals es una corazonada. Con **salida tipada** y **pruebas**, es software.

Tres piezas:
  1. ESQUEMA   — la salida es JSON tipado con un contrato claro (enums + tipos).
                 validar() rechaza cualquier respuesta que no cumpla el contrato.
  2. EVALS     — un set de casos (entrada + esperado) que mide si el prompt acierta.
  3. CICLO     — el reporte dice QUÉ caso falló y por qué, para que iteres el prompt.

Corre con **solo librería estándar** de Python 3.

Uso:
  python3 promptkit.py            # corre los evals en modo MOCK e imprime el reporte
  python3 promptkit.py --demo     # self-check: valida el contrato y que los evals corran
  OPENAI_API_KEY=... python3 promptkit.py   # usa el modelo real (salida validada igual)

ponytail: clasificación de tickets con un esquema pequeño. Para tareas con más campos
o anidados, el ESQUEMA crece (o usas jsonschema/pydantic); EVALS y CICLO no cambian.
"""
import os, sys, json, re, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.join(HERE, "data", "evals.json")


# ---------- 1. ESQUEMA (el contrato de salida) ----------
# Un prompt "software" promete una forma exacta. Esto es esa promesa, en código.
ESQUEMA = {
    "categoria": ["facturacion", "soporte_tecnico", "ventas", "otro"],
    "prioridad": ["alta", "media", "baja"],
    "requiere_humano": bool,
}


def validar(obj):
    """Devuelve el obj si cumple el contrato; si no, lanza ValueError con la razón.

    Esta es la pieza que convierte 'texto del modelo' en 'dato confiable':
    nada entra al resto del sistema sin pasar por aquí.
    """
    if not isinstance(obj, dict):
        raise ValueError(f"la salida no es un objeto JSON: {type(obj).__name__}")
    for campo, contrato in ESQUEMA.items():
        if campo not in obj:
            raise ValueError(f"falta el campo '{campo}'")
        v = obj[campo]
        if contrato is bool:
            if not isinstance(v, bool):
                raise ValueError(f"'{campo}' debe ser booleano, llegó {type(v).__name__}")
        elif v not in contrato:
            raise ValueError(f"'{campo}'={v!r} no está en {contrato}")
    extra = set(obj) - set(ESQUEMA)
    if extra:
        raise ValueError(f"campos no permitidos: {sorted(extra)}")
    return obj


# ---------- 2. EL "MODELO" (mock por reglas / LLM real) ----------
def clasificar_mock(texto):
    """Sin API key: un clasificador por reglas, transparente y determinista.

    Hace de stand-in del modelo para que los evals corran sin costo ni red.
    El modelo real (abajo) devuelve el MISMO esquema; los evals no distinguen.
    """
    t = texto.lower()
    if re.search(r"factur|cobr|pago|tarjeta|reembols|cargo", t):
        cat = "facturacion"
    elif re.search(r"error|falla|no (carga|abre|funciona)|caíd|bug|lento", t):
        cat = "soporte_tecnico"
    elif re.search(r"precio|plan|comprar|cotiz|demo|contratar", t):
        cat = "ventas"
    else:
        cat = "otro"
    if re.search(r"urgent|ya no|caíd|perdiendo|fraud|no puedo trabajar", t):
        prio = "alta"
    elif cat == "ventas" or re.search(r"cuando pued|duda|consulta", t):
        prio = "baja"
    else:
        prio = "media"
    humano = prio == "alta" or cat == "facturacion"
    return {"categoria": cat, "prioridad": prio, "requiere_humano": humano}


def clasificar_llm(texto):
    """Con OPENAI_API_KEY: el modelo responde JSON que validamos con el MISMO esquema."""
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    sys_prompt = (
        "Clasificas tickets de soporte. Responde SOLO con un objeto JSON, sin texto extra, "
        "con exactamente estas claves:\n"
        f"- categoria: una de {ESQUEMA['categoria']}\n"
        f"- prioridad: una de {ESQUEMA['prioridad']}\n"
        "- requiere_humano: true o false (booleano)\n"
    )
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": texto},
        ],
    }).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return json.loads(data["choices"][0]["message"]["content"])


def clasificar(texto):
    return clasificar_llm(texto) if os.environ.get("OPENAI_API_KEY") else clasificar_mock(texto)


# ---------- 3. EVALS + CICLO ----------
def cargar_evals(path=EVALS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluar(casos, fn=None):
    """Corre cada caso, valida la salida y la compara con lo esperado.

    Un caso PASA si la salida es válida Y todos los campos coinciden con el esperado.
    Si la salida no respeta el contrato, es FALLO 'salida inválida' (no se compara).
    """
    fn = fn or clasificar
    resultados = []
    for c in casos:
        try:
            salida = validar(fn(c["texto"]))
            diffs = [k for k in ESQUEMA if salida[k] != c["esperado"][k]]
            ok = not diffs
            razon = "" if ok else "campos distintos: " + ", ".join(diffs)
        except ValueError as e:
            salida, ok, razon = None, False, f"salida inválida: {e}"
        resultados.append({"texto": c["texto"], "esperado": c["esperado"],
                           "salida": salida, "ok": ok, "razon": razon})
    aciertos = sum(r["ok"] for r in resultados)
    return {"total": len(resultados), "aciertos": aciertos,
            "accuracy": round(aciertos / len(resultados), 3) if resultados else 0.0,
            "resultados": resultados}


def imprimir_reporte(rep):
    print(f"Evals: {rep['aciertos']}/{rep['total']} correctos "
          f"(accuracy {rep['accuracy']*100:.0f}%)\n")
    for r in rep["resultados"]:
        marca = "✓" if r["ok"] else "✗"
        print(f"  {marca} {r['texto'][:52]!r}")
        if not r["ok"]:
            print(f"      → {r['razon']}")
            print(f"        esperado: {r['esperado']}")
            print(f"        salida:   {r['salida']}")
    print("\nAsí iteras: cada ✗ te dice qué campo ajustar en el prompt/las reglas. "
          "Cambias, vuelves a correr, y ves el número subir. Eso es un prompt con evals.")


# ---------- self-check ----------
def demo():
    """Valida el contrato (acepta lo bueno, rechaza lo malo) y que los evals corran."""
    # 1. el esquema acepta una salida bien formada
    bueno = {"categoria": "ventas", "prioridad": "baja", "requiere_humano": False}
    assert validar(bueno) == bueno

    # 2. el esquema RECHAZA las 4 formas típicas en que un modelo se sale del contrato
    malos = [
        {"categoria": "spam", "prioridad": "baja", "requiere_humano": False},   # enum inválido
        {"categoria": "ventas", "prioridad": "baja"},                            # falta campo
        {"categoria": "ventas", "prioridad": "baja", "requiere_humano": "si"},   # tipo malo
        {"categoria": "ventas", "prioridad": "baja", "requiere_humano": False, "extra": 1},  # campo de más
    ]
    for m in malos:
        try:
            validar(m)
            raise AssertionError(f"debió rechazar {m}")
        except ValueError:
            pass

    # 3. los evals corren sobre el set real y el mock cumple el contrato en todos
    casos = cargar_evals()
    rep = evaluar(casos, clasificar_mock)
    assert rep["total"] == len(casos) and rep["total"] >= 6, "faltan casos de eval"
    assert all(r["salida"] is not None for r in rep["resultados"]), "el mock produjo salida inválida"
    assert rep["accuracy"] >= 0.8, f"accuracy del mock muy baja: {rep['accuracy']}"
    print(f"✓ demo OK — contrato valida y rechaza; {rep['aciertos']}/{rep['total']} evals "
          f"correctos con el mock (accuracy {rep['accuracy']*100:.0f}%)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        modo = "LLM (OPENAI_API_KEY)" if os.environ.get("OPENAI_API_KEY") else "MOCK (reglas)"
        print(f"Modo: {modo}\n")
        imprimir_reporte(evaluar(cargar_evals()))
