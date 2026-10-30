# 05 · Copiloto de IA en WhatsApp

**Estado:** En producción · **Tema:** Automatización

Donde está la gente. Un asistente que **entiende, responde y ejecuta acciones
reales** por WhatsApp — no solo chatea. El kit corre en 10 segundos con solo
Python, sin instalar nada.

## Qué vas a construir
- La **conexión al canal**: recibir el webhook de WhatsApp Cloud API y
  **verificar su firma** antes de confiar en él.
- El **cerebro** que entiende la intención del mensaje.
- Las **acciones** que puede ejecutar: consultar, agendar, escalar a un humano.

## Corre el ejemplo
```bash
cd kit
python3 copiloto.py --demo     # valida firma, parser e intenciones
python3 copiloto.py            # procesa los webhooks de muestra
```

## La idea en una línea
Un copiloto útil no es el que mejor conversa: es el que **hace cosas** de forma
segura en el canal donde ya está tu cliente. La diferencia está en las cuatro
piezas alrededor del modelo, no en el modelo.

## Los errores clásicos (honesto)
- **No verificar la firma del webhook** → cualquiera puede suplantar a Meta y
  dispararle acciones a tu copiloto. Se verifica con HMAC-SHA256 y comparación
  de tiempo constante (`hmac.compare_digest`, no `==`).
- **Asumir que todo webhook trae mensaje** → los acuses de "entregado/leído"
  (`statuses`) no traen `messages`; si no lo contemplás, revienta.
- **Match por texto exacto** → `SALDO`, `cíta` y `agéndar` deben entenderse; el
  kit pliega tildes y mayúsculas.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
