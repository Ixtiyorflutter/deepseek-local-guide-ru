# Урок 10. RAG и агенты на локальном DeepSeek

[← Урок 9](09-optimizaciya.md) · [Оглавление](../README.md) · [Урок 11 →](11-prod-i-bezopasnost.md)

## RAG: чат со своими документами

**Retrieval-Augmented Generation** — перед ответом находим релевантные куски документов и подкладываем их в промпт.

```
Документы → чанки → эмбеддинги → векторная БД
Вопрос → эмбеддинг → поиск top-k чанков → промпт с контекстом → DeepSeek → ответ
```

### Вариант без кода

Open WebUI → **Workspace → Knowledge** → загрузить PDF/DOCX → в чате `#` и выбрать базу.

### Вариант на Python (минимальный)

Полный код: [examples/rag_minimal.py](../examples/rag_minimal.py).

```bash
ollama pull bge-m3          # мультиязычные эмбеддинги, хорошо понимает русский
ollama pull deepseek-r1:14b
pip install openai numpy
python examples/rag_minimal.py
```

### Советы по качеству RAG

- **Эмбеддинги для русского:** `bge-m3`, `multilingual-e5-large`. Английские модели эмбеддингов для русского — плохо.
- **Размер чанка** 500–1000 токенов с перекрытием 10–20%.
- **Реранкер** (например, `bge-reranker-v2-m3`) после поиска заметно повышает точность.
- **Гибридный поиск** (BM25 + векторы) — лучше для терминов, артикулов, имён.
- С V4 и контекстом 1M небольшую базу (десятки документов) можно **просто положить в контекст целиком** — без RAG.
- Проси модель **цитировать источник** каждого факта.

## Tool calling (вызов функций)

Ollama, llama-server (`--jinja`) и vLLM поддерживают `tools` в формате OpenAI.

```python
tools = [{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "Погода в городе",
    "parameters": {
      "type": "object",
      "properties": {"city": {"type": "string"}},
      "required": ["city"]
    }
  }
}]

resp = client.chat.completions.create(
    model="deepseek-r1:14b",  # или V4-Flash через llama-server
    messages=[{"role": "user", "content": "Какая погода в Казани?"}],
    tools=tools,
)
print(resp.choices[0].message.tool_calls)
```

Полный цикл «модель → функция → модель» — [examples/tool_calling.py](../examples/tool_calling.py).

> ⚠️ Маленькие дистилляты вызывают инструменты нестабильно. Для надёжных агентов — 14B+ или V4. Проверь, что шаблон модели поддерживает tools (`ollama show <модель>`).

## Фреймворки

| Фреймворк | Для чего | Подключение DeepSeek |
|---|---|---|
| **LangChain / LangGraph** | Цепочки, агенты с графом состояний | `ChatOllama(model="deepseek-r1:14b")` или `ChatOpenAI(base_url=...)` |
| **LlamaIndex** | RAG, индексация документов | `Ollama(model=...)` |
| **smolagents** | Лёгкие код-агенты | `OpenAIServerModel(api_base=...)` |
| **CrewAI** | Мульти-агентные команды | `LLM(model="ollama/deepseek-r1:14b")` |
| **MCP** | Подключение инструментов к агентам по стандарту | Через клиент, поддерживающий OpenAI-совместимые модели |

## Паттерн «думающий планировщик + быстрый исполнитель»

- **Планировщик:** V4 / R1-32B в режиме размышлений — разбивает задачу на шаги.
- **Исполнитель:** та же модель в no-think или маленькая модель — быстро выполняет шаги и вызывает инструменты.

Так экономятся время и токены: дорогое рассуждение — один раз.

[Урок 11: Продакшн и безопасность →](11-prod-i-bezopasnost.md)
