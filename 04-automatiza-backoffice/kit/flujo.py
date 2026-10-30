#!/usr/bin/env python3
"""Automatiza tu backoffice — kit de La Bóveda (Esteban Baquero).

El tiempo que más se pierde en una operación es MOVER datos de un lado a otro:
leer un correo, decidir qué hacer, y registrar/responder/avisar. Esto lo
automatiza con criterio, en tres piezas:

  1) DISPARADOR  — de dónde entra el trabajo (correo, archivo, webhook).
                   Aquí lo simulamos leyendo entradas/*.json.
  2) DECISIÓN    — reglas declarativas en reglas.json (sin tocar código).
  3) ACCIÓN      — qué se hace: registrar, responder, avisar, escalar.

Corre con **solo librería estándar** de Python. Sin dependencias.

Uso:
  python3 flujo.py --demo              # self-check: valida el motor de reglas
  python3 flujo.py                     # procesa todo entradas/ y muestra el plan
  python3 flujo.py --aplicar           # igual, pero "ejecuta" las acciones (simulado)

ponytail: el disparador y las acciones son simulados (leen archivos / escriben a
un log). Para producción, conectá el disparador a tu IMAP/webhook real y las
acciones a tu API/CRM/Slack — la lógica de decisión (abajo) no cambia.
"""
import os, re, sys, json, glob, unicodedata, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REGLAS = os.path.join(HERE, "reglas.json")
ENTRADAS = os.path.join(HERE, "entradas")
LOG = os.path.join(HERE, "acciones.log")


def fold(s):
    """minúsculas sin tildes: 'Envíos' -> 'envios' (match robusto)."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def cumple(cond, entrada):
    """Evalúa UNA condición de regla contra la entrada. Operadores soportados."""
    campo = entrada.get(cond["campo"])
    op = cond["op"]
    val = cond["valor"]
    if op == "contiene":
        return fold(val) in fold(campo)
    if op == "igual":
        return fold(campo) == fold(val)
    if op == "mayor":          # numérico
        return _num(campo) > _num(val)
    if op == "menor":
        return _num(campo) < _num(val)
    if op == "en":             # valor del campo está en una lista
        return fold(campo) in [fold(v) for v in val]
    raise ValueError(f"operador desconocido: {op}")


def _num(x):
    """Extrae número de '$ 1.250.000' o 1250000 → 1250000.0. Formato CO."""
    if isinstance(x, (int, float)):
        return float(x)
    s = re.sub(r"[^\d,.-]", "", str(x))
    # miles con punto, decimal con coma (es-CO): 1.250.000,50
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "") if s.count(".") > 1 else s
    try:
        return float(s)
    except ValueError:
        return 0.0


def decidir(entrada, reglas):
    """Primera regla cuyas condiciones (TODAS) se cumplen gana. Si ninguna, default."""
    for regla in reglas["reglas"]:
        if all(cumple(c, entrada) for c in regla["si"]):
            return regla["entonces"], regla["nombre"]
    return reglas["default"], "default"


def ejecutar(accion, entrada, aplicar):
    """La ACCIÓN final. En este kit se simula; en prod conectás tu API aquí."""
    tipo = accion["accion"]
    msg = accion.get("mensaje", "").format(**entrada)
    linea = f"{entrada.get('id','?')} :: {tipo.upper()} :: {msg}"
    if aplicar:
        with open(LOG, "a", encoding="utf-8") as f:
            ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
            f.write(f"{ts}  {linea}\n")
    return linea


def cargar_entradas():
    out = []
    for p in sorted(glob.glob(os.path.join(ENTRADAS, "*.json"))):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def correr(aplicar=False):
    with open(REGLAS, encoding="utf-8") as f:
        reglas = json.load(f)
    entradas = cargar_entradas()
    print(f"→ {len(entradas)} entradas · {len(reglas['reglas'])} reglas\n")
    for e in entradas:
        accion, nombre = decidir(e, reglas)
        linea = ejecutar(accion, e, aplicar)
        print(f"  [{nombre}]  {linea}")
    if aplicar:
        print(f"\n✓ acciones registradas en {os.path.basename(LOG)}")


# ---------------------------------------------------------------- self-check
def demo():
    """Valida el motor de decisión con casos que un modelo descuidado erraría."""
    reglas = {
        "reglas": [
            {"nombre": "factura-alta", "si": [
                {"campo": "tipo", "op": "igual", "valor": "factura"},
                {"campo": "monto", "op": "mayor", "valor": 1000000}],
             "entonces": {"accion": "escalar", "mensaje": "aprobar {proveedor}"}},
            {"nombre": "soporte-urgente", "si": [
                {"campo": "asunto", "op": "contiene", "valor": "urgente"}],
             "entonces": {"accion": "avisar", "mensaje": "ping a soporte"}},
            {"nombre": "factura-normal", "si": [
                {"campo": "tipo", "op": "igual", "valor": "factura"}],
             "entonces": {"accion": "registrar", "mensaje": "al ERP"}},
        ],
        "default": {"accion": "revisar", "mensaje": "cola manual"},
    }

    # 1) factura grande → escala (y gana sobre factura-normal por orden)
    a, n = decidir({"tipo": "Factura", "monto": "$ 2.500.000"}, reglas)
    assert n == "factura-alta", n

    # 2) factura chica → registrar (cae a la segunda regla de factura)
    a, n = decidir({"tipo": "factura", "monto": 50000}, reglas)
    assert n == "factura-normal", n
    assert a["accion"] == "registrar"

    # 3) tildes y mayúsculas no rompen el match ('URGENTE' vs 'urgente')
    a, n = decidir({"tipo": "correo", "asunto": "Caso URGENTE de envíos"}, reglas)
    assert n == "soporte-urgente", n

    # 4) nada matchea → default, no explota
    a, n = decidir({"tipo": "otro"}, reglas)
    assert n == "default" and a["accion"] == "revisar", (n, a)

    # 5) parser de monto formato CO (puntos de miles) es correcto
    assert _num("$ 1.250.000") == 1250000.0
    assert _num("1.250.000,50") == 1250000.50
    assert _num(0) == 0.0

    # 6) operador 'en' (lista)
    r = {"reglas": [{"nombre": "vip", "si": [
        {"campo": "cliente", "op": "en", "valor": ["Acme", "Globex"]}],
        "entonces": {"accion": "avisar"}}], "default": {"accion": "x"}}
    assert decidir({"cliente": "acme"}, r)[1] == "vip"

    print("✓ demo OK — 6 casos (orden de reglas, tildes, parser CO, default, 'en')")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        correr(aplicar="--aplicar" in sys.argv)
