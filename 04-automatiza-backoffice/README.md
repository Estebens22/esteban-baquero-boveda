# 04 · Automatiza tu backoffice

**Estado:** En producción · **Tema:** Automatización

Deja de copiar y pegar: un flujo que **lee, decide y actúa** sobre tus tareas
repetitivas. Disparador → lógica de decisión → acción final. El kit corre en 10
segundos con solo Python, sin instalar nada.

## Qué vas a construir
- El **disparador** (correo, archivo, webhook) que mete el trabajo al flujo.
- La **lógica de decisión** en reglas declarativas — las editas sin tocar código.
- La **acción final**: registrar, responder, avisar o escalar.

## Corre el ejemplo
```bash
cd kit
python3 flujo.py --demo        # valida el motor de reglas
python3 flujo.py               # procesa las entradas de muestra
```

## La idea en una línea
La mayoría del tiempo perdido es **mover datos de un lado a otro**. Esto no es
"un script más": es separar las tres piezas (disparo, decisión, acción) para
que cambies las reglas sin reprogramar y conectes cada pieza a lo tuyo.

## Los errores clásicos (honesto)
- **Reglas en el orden equivocado** → una regla general se come a la específica. El motor evalúa en orden; específicas arriba.
- **Match frágil por tildes/mayúsculas** → el kit pliega acentos y caso.
- **Comparar montos como texto** → `$ 1.250.000` se parsea a número antes de comparar.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Sígueme y dale ⭐ en GitHub](https://github.com/Estebens22)
