# 10 · Prompts que se comportan como software

**Estado:** Prototipo · **Tema:** Fine-tuning

Un prompt sin evals es una corazonada. Con **salida tipada** y **pruebas**, es software: sabes cuándo mejora, cuándo empeora y por qué. El kit corre en 10 segundos con solo Python.

## Qué vas a construir
- La **salida tipada**: un contrato de JSON (enums + tipos) que el `validar()` hace cumplir. Nada entra al sistema sin pasar por ahí.
- Los **evals**: un set de casos (entrada + esperado) que mide si el prompt acierta.
- El **ciclo de mejora**: el reporte te dice QUÉ caso falló y por qué, para que iteres el prompt y veas el número subir.

## Corre el ejemplo
```bash
cd kit
python3 promptkit.py --demo
python3 promptkit.py
```
Sin API key corre en modo **MOCK** (un clasificador por reglas que hace de stand-in del modelo). Con `OPENAI_API_KEY` usa el modelo real — y la salida pasa por **el mismo** `validar()`.

```bash
OPENAI_API_KEY=sk-... python3 promptkit.py
```

## La idea en una línea
El modelo propone; el **esquema dispone**. Validas la salida contra un contrato y la mides contra evals: así un prompt deja de ser magia y se vuelve una pieza de software que puedes mejorar con método.

## Los errores clásicos (honesto)
- **Confiar en el texto del modelo tal cual** → tarde o temprano devuelve algo fuera de contrato y te rompe el sistema. Valida siempre.
- **"Se ve bien" como prueba** → sin evals no sabes si tu cambio al prompt ayudó o empeoró. Mide.
- **Evals solo de casos fáciles** → mete los ambiguos y los límite; ahí es donde el prompt se cae.
- **Mover el esquema cada semana** → el contrato es una promesa. Cámbialo con intención, no por inercia.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
