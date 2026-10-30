# 03 · Asistente RAG sobre tus documentos

**Estado:** En producción · **Tema:** RAG

Un asistente que responde sobre **TUS** documentos: ingesta → recuperación → respuesta **con citas**, sin inventar. Aprendé haciendo: el kit corre en 10 segundos con solo Python.

## Qué vas a construir
- La **ingesta** y el troceado de tus documentos.
- La **recuperación** (TF-IDF + coseno, sin vector DB ni dependencias).
- La **respuesta con citas** a la fuente — modo MOCK sin API key, o LLM real con `OPENAI_API_KEY`.

## Corré el ejemplo
```bash
cd kit
python3 rag.py --demo
python3 rag.py "¿cuál es la política de devoluciones?"
```

## La idea en una línea
RAG no es "meter todo en el prompt": es **buscar lo relevante en tus datos** y dejar que el modelo responda con esa evidencia. Así no alucina y podés auditar de dónde salió cada afirmación.

## Los errores clásicos (honesto)
- **Chunks sin solape** → se corta el contexto a la mitad. Por eso el kit usa solape.
- **Pregunta con tildes vs documento sin tildes** → se pliegan acentos para que coincidan.
- **El modelo responde de más** → el system prompt lo obliga a usar solo la evidencia y citar.

---
**Esteban Baquero** — De una idea a un sistema que funciona.
¿Te sirvió? [Seguime y dale ⭐ en GitHub](https://github.com/Estebens22)
