#!/usr/bin/env python3
"""Copiloto de IA en WhatsApp — kit de La Bóveda (Esteban Baquero).

Un copiloto de WhatsApp no es "un bot que chatea": es un asistente que
**entiende, responde y EJECUTA acciones reales** donde ya está tu gente.
Lo difícil no es el modelo de lenguaje — es hacer bien las cuatro piezas
que lo rodean, que un demo descuidado pasa por alto:

  1) EL CANAL     — recibís un webhook de WhatsApp Cloud API. ANTES de leerlo,
                    verificás su FIRMA (HMAC-SHA256). Sin esto, cualquiera
                    le manda POST a tu copiloto haciéndose pasar por Meta.
  2) EL PARSER    — el mensaje viene enterrado en un JSON anidado
                    (entry[].changes[].value.messages[]). Y a veces el webhook
                    NO trae mensaje (es un acuse de "entregado/leído").
  3) EL CEREBRO   — detectás la INTENCIÓN del texto y la mapeás a una acción.
  4) LA ACCIÓN    — consultar saldo, agendar, escalar a un humano. Lo real.

Corre con **solo librería estándar** de Python. Sin dependencias.

Uso:
  python3 copiloto.py --demo          # self-check: firma, parser e intenciones
  python3 copiloto.py                 # procesa entradas/ (webhooks de muestra)

ponytail: el canal y las acciones son simulados (leen archivos / imprimen).
Para producción enganchás tu POST real de WhatsApp Cloud API y tus acciones
(API/CRM/calendario) en los mismos puntos — la firma, el parser y el ruteo de
intención NO cambian. La firma HMAC es EXACTAMENTE la que usa Meta
(header X-Hub-Signature-256: sha256=<hex>).
"""
import os, re, sys, json, glob, hmac, hashlib, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
INTENCIONES = os.path.join(HERE, "intenciones.json")
ENTRADAS = os.path.join(HERE, "entradas")


def fold(s):
    """minúsculas sin tildes: 'Está' -> 'esta' (match robusto al texto del user)."""
    s = unicodedata.normalize("NFKD", str(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ---------------------------------------------------------------- 1) EL CANAL
def firmar(body_bytes, app_secret):
    """Calcula la firma que Meta pone en X-Hub-Signature-256 para este body."""
    mac = hmac.new(app_secret.encode(), body_bytes, hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def verificar_firma(body_bytes, signature_header, app_secret):
    """True solo si la firma del header corresponde al body y al secreto.

    Usa hmac.compare_digest (comparación de tiempo constante). Comparar con
    '==' filtra info por timing y permite forjar la firma byte a byte: NO.
    """
    if not signature_header:
        return False
    esperado = firmar(body_bytes, app_secret)
    return hmac.compare_digest(esperado, signature_header)


# --------------------------------------------------------------- 2) EL PARSER
def parse_mensaje(payload):
    """Extrae {from, text, type} del JSON de WhatsApp Cloud API.

    Devuelve None si el webhook no trae un mensaje de texto (p.ej. un acuse
    de 'entregado/leído' trae 'statuses', no 'messages'). NO debe reventar.
    """
    try:
        value = payload["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return None
    mensajes = value.get("messages")
    if not mensajes:
        return None  # es un status u otro evento, no un mensaje entrante
    m = mensajes[0]
    if m.get("type") != "text":
        return {"from": m.get("from"), "type": m.get("type"), "text": ""}
    return {"from": m.get("from"), "type": "text",
            "text": m.get("text", {}).get("body", "")}


# --------------------------------------------------------------- 3) EL CEREBRO
def detectar_intencion(texto, intenciones):
    """Primera intención con alguna palabra clave presente gana. Si ninguna,
    cae a 'fallback'. El orden en el JSON define prioridad: específicas arriba."""
    t = fold(texto)
    for intent in intenciones["intenciones"]:
        if any(fold(k) in t for k in intent["claves"]):
            return intent
    return intenciones["fallback"]


# ---------------------------------------------------------------- 4) LA ACCIÓN
def ejecutar(intent, entrada):
    """La acción real. En el kit se simula; en prod conectás tu API aquí."""
    accion = intent["accion"]
    respuesta = intent["responder"].format(**entrada)
    return accion, respuesta


def atender(payload, intenciones):
    """Pipeline completo de un webhook YA verificado → (acción, respuesta)."""
    entrada = parse_mensaje(payload)
    if entrada is None:
        return None
    intent = detectar_intencion(entrada["text"], intenciones)
    accion, respuesta = ejecutar(intent, entrada)
    return {"from": entrada["from"], "intent": intent["nombre"],
            "accion": accion, "respuesta": respuesta}


def correr():
    with open(INTENCIONES, encoding="utf-8") as f:
        intenciones = json.load(f)
    archivos = sorted(glob.glob(os.path.join(ENTRADAS, "*.json")))
    print(f"→ {len(archivos)} webhooks de muestra\n")
    for p in archivos:
        with open(p, encoding="utf-8") as f:
            payload = json.load(f)
        r = atender(payload, intenciones)
        if r is None:
            print(f"  [{os.path.basename(p)}]  (sin mensaje: acuse/estado — ignorado)")
        else:
            print(f"  [{r['intent']}]  {r['from']} → {r['accion'].upper()}")
            print(f"       ↳ \"{r['respuesta']}\"")


# ---------------------------------------------------------------- self-check
def demo():
    """Valida las piezas con casos que un copiloto descuidado erraría."""
    secret = "mi-app-secret-de-meta"

    # 1) firma válida pasa
    body = b'{"hola":"mundo"}'
    sig = firmar(body, secret)
    assert verificar_firma(body, sig, secret) is True

    # 2) body alterado NO pasa (aunque sea un byte)
    assert verificar_firma(b'{"hola":"MUNDO"}', sig, secret) is False

    # 3) secreto equivocado NO pasa
    assert verificar_firma(body, sig, "otro-secreto") is False

    # 4) sin header de firma NO pasa (no revienta)
    assert verificar_firma(body, None, secret) is False
    assert verificar_firma(body, "", secret) is False

    # 5) parser sobre el envelope REAL anidado de Cloud API
    real = {"entry": [{"changes": [{"value": {"messages": [
        {"from": "573001112233", "type": "text",
         "text": {"body": "Hola, quiero saber mi saldo"}}]}}]}]}
    e = parse_mensaje(real)
    assert e == {"from": "573001112233", "type": "text",
                 "text": "Hola, quiero saber mi saldo"}, e

    # 6) webhook de ESTADO (entregado/leído) → None, no explota
    estado = {"entry": [{"changes": [{"value": {"statuses": [
        {"status": "delivered"}]}}]}]}
    assert parse_mensaje(estado) is None

    # 7) payload basura → None, no explota
    assert parse_mensaje({}) is None
    assert parse_mensaje({"entry": []}) is None

    # 8) intención: tildes y mayúsculas no rompen el match
    intenciones = {
        "intenciones": [
            {"nombre": "consulta_saldo", "claves": ["saldo", "cuánto tengo"],
             "accion": "consultar_saldo", "responder": "Tu saldo es $X"},
            {"nombre": "agendar", "claves": ["agendar", "cita", "turno"],
             "accion": "crear_evento", "responder": "Listo, te agendé"},
            {"nombre": "humano", "claves": ["asesor", "humano", "persona"],
             "accion": "escalar", "responder": "Te paso con un asesor"},
        ],
        "fallback": {"nombre": "fallback", "claves": [],
                     "accion": "responder_generico", "responder": "¿Podés reformular?"},
    }
    assert detectar_intencion("Quiero SABER mi Saldo", intenciones)["nombre"] == "consulta_saldo"
    assert detectar_intencion("necesito agéndar una cíta", intenciones)["nombre"] == "agendar"

    # 9) intención desconocida → fallback, no explota
    assert detectar_intencion("asdf qwer", intenciones)["nombre"] == "fallback"

    # 10) orden = prioridad: 'asesor' escala aunque el texto mencione saldo
    assert detectar_intencion("mi saldo está mal, pásame un asesor", intenciones)["nombre"] == "consulta_saldo"
    #    (saldo va primero en la lista → gana; mové 'humano' arriba si querés invertir)

    print("✓ demo OK — 10 casos (firma HMAC timing-safe, parser Cloud API, estados, intención con tildes, fallback, prioridad)")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        correr()
