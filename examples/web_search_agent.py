"""
Локальный DeepSeek (Ollama) + официальный DeepSeek Search/Fetch API как инструменты.
Модель думает у вас на компьютере, свежие данные берёт из веб-поиска DeepSeek.

    export DEEPSEEK_API_KEY=sk-...
    pip install openai requests
    python web_search_agent.py "Что нового в DeepSeek V4.1-Flash-1017?"

Документация API: https://api-docs.deepseek.com/guides/search
"""
import json
import os
import sys

import requests
from openai import OpenAI

LOCAL = OpenAI(base_url=os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1"), api_key="ollama")
MODEL = os.getenv("LOCAL_MODEL", "deepseek-r1:14b")
DS = "https://api.deepseek.com/v1/tools"
HEADERS = {"Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY', '')}"}


def web_search(query: str, count: int = 5) -> list[dict]:
    r = requests.post(f"{DS}/search", headers=HEADERS, timeout=30,
                      json={"query": query[:128], "count": count})
    r.raise_for_status()
    return [
        {"title": x["title"], "url": x["url"], "date": x.get("date"), "summary": x.get("summary", "")}
        for x in r.json().get("results", [])
        if x.get("rerank_score", 0) >= 1.0
    ]


def fetch_page(url: str) -> dict:
    r = requests.post(f"{DS}/fetch", headers=HEADERS, timeout=60, json={"url": url})
    r.raise_for_status()
    d = r.json()
    return {"title": d.get("title", ""), "content": d.get("content", "")[:8000]}


FUNCS = {"web_search": web_search, "fetch_page": fetch_page}
TOOLS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Поиск в интернете. Поддерживает операторы site:, lang:ru, after:2026-01-01",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "count": {"type": "integer"}}, "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "fetch_page",
        "description": "Скачать страницу по URL и получить текст в Markdown",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
]

SYSTEM = ("Ты исследователь. Для фактов о текущих событиях используй web_search, "
          "при необходимости открой страницу через fetch_page. Отвечай на русском, "
          "в конце перечисли источники (URL).")


def ask(question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(6):
        msg = LOCAL.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            print(f"  🔎 {call.function.name}({args})", file=sys.stderr)
            try:
                result = FUNCS[call.function.name](**args)
            except Exception as e:  # отдаём ошибку модели, пусть попробует иначе
                result = {"error": str(e)}
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "content": json.dumps(result, ensure_ascii=False)})
    return "Превышен лимит шагов"


if __name__ == "__main__":
    print(ask(" ".join(sys.argv[1:]) or "Какие модели DeepSeek вышли в 2026 году?"))
