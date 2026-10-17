"""
Минимальный RAG на локальном DeepSeek без векторных БД.

    ollama pull bge-m3
    ollama pull deepseek-r1:14b
    pip install openai numpy
    python rag_minimal.py --docs ./my_docs --question "Какой срок оплаты по договору?"

Кладите в папку .txt или .md файлы.
"""
import argparse
import pathlib

import numpy as np
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
EMBED_MODEL = "bge-m3"


def chunk(text: str, size: int = 1500, overlap: int = 200) -> list[str]:
    out, i = [], 0
    while i < len(text):
        out.append(text[i : i + size])
        i += size - overlap
    return out


def embed(texts: list[str]) -> np.ndarray:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = np.array([d.embedding for d in resp.data], dtype=np.float32)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--docs", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--model", default="deepseek-r1:14b")
    p.add_argument("--top-k", type=int, default=4)
    args = p.parse_args()

    chunks, sources = [], []
    for f in pathlib.Path(args.docs).rglob("*"):
        if f.suffix.lower() in {".txt", ".md"}:
            for c in chunk(f.read_text(encoding="utf-8", errors="ignore")):
                chunks.append(c)
                sources.append(f.name)
    if not chunks:
        raise SystemExit("Не найдено .txt/.md файлов")

    doc_vecs = embed(chunks)
    q_vec = embed([args.question])[0]
    top = np.argsort(doc_vecs @ q_vec)[::-1][: args.top_k]

    context = "\n\n".join(f"[{i + 1}] ({sources[j]})\n{chunks[j]}" for i, j in enumerate(top))
    prompt = (
        f"Контекст:\n{context}\n\n"
        f"Вопрос: {args.question}\n\n"
        "Ответь на русском, опираясь ТОЛЬКО на контекст. "
        "После каждого факта укажи номер источника в квадратных скобках. "
        "Если ответа в контексте нет — так и скажи."
    )
    resp = client.chat.completions.create(
        model=args.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    print(resp.choices[0].message.content)


if __name__ == "__main__":
    main()
