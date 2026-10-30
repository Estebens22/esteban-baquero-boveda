# 07 · Dashboard que decide con IA

**Estado:** En producción · **Tema:** Automatización

Un tablero que no solo muestra números: los **interpreta** y sugiere la siguiente acción. Aprende haciendo: el kit corre en 10 segundos con solo Python y genera un dashboard que lees en el navegador.

## Qué vas a construir
- La **carga** de datos (un CSV de ventas; luego lo cambias por tu base de datos).
- La **capa de KPIs y señales** — el código calcula las cifras exactas y detecta banderas.
- Las **recomendaciones accionables** — modo reglas sin API key, o el modelo con `OPENAI_API_KEY`.

## Corre el ejemplo
```bash
cd kit
python3 dashboard.py --demo
python3 dashboard.py
```
Abre el `dashboard.html` que se genera.

## La idea en una línea
Los datos solos no deciden. El **código hace la aritmética** (exacta, auditable) y el **modelo pone el criterio** — le pasas las cifras ya calculadas, no la tabla cruda, para que no invente números.

## Los errores clásicos (honesto)
- **Mandarle la tabla cruda al modelo** → alucina sumas. Mándale los KPIs ya calculados.
- **Sugerir diez cosas** → un dashboard que recomienda todo no decide nada. Una sola acción.
- **Acciones no medibles** → "sube el presupuesto" no sirve; "baja ads 15% y mide ROAS a 7 días" sí.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
