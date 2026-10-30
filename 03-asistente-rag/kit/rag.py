#!/usr/bin/env python3
"""Asistente RAG sobre tus documentos — kit de La Bóveda (Esteban Baquero).

RAG = recuperar los trozos relevantes de TUS documentos y dejar que el modelo
responda CON esa evidencia (citando), en vez de inventar.

Este kit corre con **solo librería estándar** de Python:
  - Ingesta: lee docs/*.md|*.txt, los trocea en chunks.
  - Recuperación: TF-IDF + similitud coseno (sin numpy, sin vector DB).
  - Respuesta: modo MOCK (extractivo, sin API key) o LLM real si hay OPENAI_API_KEY.

Uso:
  python3 rag.py "¿Cuál es la política de devoluciones?"
  python3 rag.py --demo        # self-check: valida que la recuperación acierta

ponytail: TF-IDF en memoria. Para >~5k chunks o producción, pasar a embeddings +
un índice (faiss/sqlite-vss). Para este tamaño, TF-IDF es suficiente y sin deps.
"""
import os, re, sys, math, glob, json, unicodedata, urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "docs")
TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text):
    # plegar acentos (envíos -> envios) para que el usuario escriba sin tildes
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
    return TOKEN.findall(text)


def chunk(text, size=60, overlap=15):
    """Trocea por palabras con solape (mantiene contexto entre chunks)."""
    words = text.split()
    if not words:
        return []
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        i += size - overlap
    return out


def load_chunks():
    chunks = []
    for path in sorted(glob.glob(os.path.join(DOCS, "*.md")) + glob.glob(os.path.join(DOCS, "*.txt"))):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            for j, c in enumerate(chunk(f.read())):
                chunks.append({"source": name, "n": j, "text": c})
    return chunks


def build_index(chunks):
    """Vocabulario + IDF + vectores TF-IDF por chunk."""
    df = Counter()
    docs_tokens = []
    for c in chunks:
        toks = tokenize(c["text"])
        docs_tokens.append(toks)
        for t in set(toks):
            df[t] += 1
    N = max(1, len(chunks))
    idf = {t: math.log((N + 1) / (df[t] + 1)) + 1 for t in df}
    vecs = []
    for toks in docs_tokens:
        tf = Counter(toks)
        v = {t: (tf[t] / len(toks)) * idf[t] for t in tf} if toks else {}
        vecs.append(v)
    return idf, vecs


def vec_for(text, idf):
    toks = tokenize(text)
    if not toks:
        return {}
    tf = Counter(toks)
    return {t: (tf[t] / len(toks)) * idf.get(t, 0.0) for t in tf}


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(a[t] * b.get(t, 0.0) for t in a)
    na = math.sqrt(sum(x * x for x in a.values()))
    nb = math.sqrt(sum(x * x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def retrieve(query, chunks, idf, vecs, k=3):
    q = vec_for(query, idf)
    scored = sorted(
        ({**c, "score": cosine(q, vecs[i])} for i, c in enumerate(chunks)),
        key=lambda c: c["score"], reverse=True,
    )
    return [c for c in scored if c["score"] > 0][:k]


def answer_mock(query, hits):
    """Sin API key: respuesta extractiva honesta (muestra la evidencia + de dónde salió)."""
    if not hits:
        return "No encontré nada relevante en tus documentos para esa pregunta."
    partes = [f"• ({h['source']}#{h['n']}, score {h['score']:.2f})\n  {h['text']}" for h in hits]
    return ("Según tus documentos (modo MOCK, sin LLM):\n\n" + "\n\n".join(partes) +
            "\n\nℹ️  Con OPENAI_API_KEY, el modelo redacta una respuesta citando estas fuentes.")


def answer_llm(query, hits):
    """Con OPENAI_API_KEY: el modelo responde SOLO con la evidencia recuperada."""
    key = os.environ["OPENAI_API_KEY"]
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    ctx = "\n\n".join(f"[{h['source']}#{h['n']}]\n{h['text']}" for h in hits)
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "Responde SOLO con la evidencia dada. Cita las fuentes como [archivo#n]. Si la evidencia no alcanza, dilo."},
            {"role": "user", "content": f"Evidencia:\n{ctx}\n\nPregunta: {query}"},
        ],
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(f"{base}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]["content"]


def ask(query, k=3):
    chunks = load_chunks()
    if not chunks:
        return "No hay documentos en docs/. Agregá .md o .txt y reintentá."
    idf, vecs = build_index(chunks)
    hits = retrieve(query, chunks, idf, vecs, k)
    if os.environ.get("OPENAI_API_KEY"):
        try:
            return answer_llm(query, hits) + "\n\nFuentes: " + ", ".join(f"{h['source']}#{h['n']}" for h in hits)
        except Exception as e:
            return f"(LLM falló: {e}\nCaigo a modo MOCK)\n\n" + answer_mock(query, hits)
    return answer_mock(query, hits)


def demo():
    """Self-check: con los docs de muestra, 'devoluciones' debe recuperar el doc de política."""
    chunks = load_chunks()
    assert chunks, "faltan docs de muestra"
    idf, vecs = build_index(chunks)
    hits = retrieve("política de devoluciones y reembolsos", chunks, idf, vecs, 3)
    assert hits, "la recuperación no devolvió nada"
    top = hits[0]["source"].lower()
    assert "devolucion" in top or "politica" in top, f"esperaba el doc de políticas, salió {top}"
    print(f"✓ demo OK — top chunk: {hits[0]['source']}#{hits[0]['n']} (score {hits[0]['score']:.2f})")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    elif len(sys.argv) > 1:
        print(ask(" ".join(sys.argv[1:])))
    else:
        print(__doc__)
