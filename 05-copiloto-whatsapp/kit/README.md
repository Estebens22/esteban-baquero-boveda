# Kit · Copiloto de IA en WhatsApp

Un copiloto que **entiende, responde y ejecuta acciones** por WhatsApp. Corre
con **solo Python** (librería estándar). Sin dependencias.

## Corre el ejemplo (10 segundos)
```bash
python3 copiloto.py --demo     # self-check: firma, parser e intenciones
python3 copiloto.py            # procesa los webhooks de muestra de entradas/
```

## Qué hay dentro
- **`copiloto.py`** — las 4 piezas: verifica la firma, parsea el webhook,
  detecta la intención, ejecuta la acción.
- **`intenciones.json`** — tus intenciones y respuestas. **Editás esto, no el código.**
- **`entradas/*.json`** — webhooks de muestra en el formato **real** de
  WhatsApp Cloud API (incluye un acuse de estado para probar el caso borde).

## Las 4 piezas (y los errores que casi todos cometen)
1. **El canal — verificá la firma SIEMPRE.** Meta firma cada webhook con
   HMAC-SHA256 en el header `X-Hub-Signature-256: sha256=<hex>`. Si no la
   verificás, cualquiera le pega un POST a tu endpoint fingiendo ser Meta.
   El kit la compara con `hmac.compare_digest` (tiempo constante) — comparar
   con `==` filtra la firma byte a byte.
2. **El parser — el mensaje viene anidado.** Está en
   `entry[0].changes[0].value.messages[0]`. Y a veces el webhook **no trae
   mensaje**: es un acuse de "entregado/leído" (`statuses`). Si no lo
   contemplás, tu copiloto revienta con cada acuse.
3. **El cerebro — intención, no palabras exactas.** Se pliegan tildes y
   mayúsculas (`SALDO` = `saldo`, `cíta` = `cita`). El orden en el JSON es la
   prioridad: la primera intención que matchea gana.
4. **La acción — lo real.** Consultar saldo, agendar, escalar a un humano. En
   el kit se imprime; en producción conectás tu API/CRM/calendario ahí mismo.

## Agrega una intención (sin tocar código)
En `intenciones.json`, dentro de `"intenciones"`:
```json
{
  "nombre": "estado_pedido",
  "claves": ["pedido", "mi orden", "dónde está mi compra"],
  "accion": "consultar_pedido",
  "responder": "Tu pedido va en camino, llega hoy 📦"
}
```
Ponelo **arriba** si debe ganarle a intenciones más generales.

## De este kit a producción
Reemplazas el "disparador de archivos" por tu endpoint POST real (el que
registrás en Meta), verificás la firma con tu `APP_SECRET`, y en `ejecutar()`
enganchas tus acciones reales. La firma, el parser y el ruteo **no cambian**.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
