# Kit · Automatiza tu backoffice

Un flujo que **lee, decide y actúa** sobre tareas repetitivas. Tres piezas:
disparador → decisión → acción. Corre con **solo Python** (librería estándar).

## Corré el ejemplo (10 segundos)
```bash
python3 flujo.py --demo        # self-check: valida el motor de reglas
python3 flujo.py               # procesa entradas/ y muestra el plan
python3 flujo.py --aplicar     # "ejecuta" las acciones (las escribe a acciones.log)
```

## Qué hay dentro
- **`flujo.py`** — el motor: lee las entradas, evalúa las reglas, decide la acción.
- **`reglas.json`** — tus reglas de decisión. **Editás esto, no el código.**
- **`entradas/*.json`** — entradas de muestra (facturas, correos, un webhook).

## Cómo funciona
1. **Disparador:** aquí lee `entradas/*.json`. En producción lo conectás a tu
   IMAP, una carpeta vigilada o un webhook — cada mensaje es una entrada.
2. **Decisión:** `reglas.json` se evalúa **en orden**; la primera regla cuyas
   condiciones se cumplen gana. Operadores: `contiene`, `igual`, `mayor`,
   `menor`, `en`. Si ninguna aplica → `default`.
3. **Acción:** `escalar`, `avisar`, `registrar`, `responder`, `revisar`. En el
   kit se imprimen/loguean; en producción conectás tu API/CRM/Slack ahí.

## Agregá una regla (sin tocar código)
En `reglas.json`, dentro de `"reglas"`:
```json
{
  "nombre": "pago-proveedor-recurrente",
  "si": [{ "campo": "proveedor", "op": "en", "valor": ["Acme", "Globex"] }],
  "entonces": { "accion": "registrar", "mensaje": "Pago programado a {proveedor}" }
}
```

## Los errores clásicos (honesto)
- **Orden de reglas:** la primera que matchea gana. Poné las específicas arriba
  (factura grande) y las generales abajo (factura normal).
- **Tildes y mayúsculas:** se pliegan (`URGENTE` = `urgente`, `envíos` = `envios`)
  para que el match no dependa de cómo venga escrito.
- **Montos con formato CO:** `$ 1.250.000` se parsea a número; no compares texto.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Seguime y dale ⭐ en GitHub](https://github.com/Estebens22)
