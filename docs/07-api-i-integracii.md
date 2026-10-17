# Урок 7. API и интеграции: подключаем локальный DeepSeek к коду и IDE

[← Урок 6](06-interfeisy.md) · [Оглавление](../README.md) · [Урок 8 →](08-promptting.md)

## Единый принцип: OpenAI-совместимый API

| Бэкенд | `base_url` |
|---|---|
| Ollama | `http://localhost:11434/v1` |
| llama-server | `http://localhost:8080/v1` |
| LM Studio | `http://localhost:1234/v1` |
| vLLM | `http://localhost:8000/v1` |
| SGLang | `http://localhost:30000/v1` |
| Официальный API DeepSeek | `https://api.deepseek.com` |

Меняешь только `base_url` и `model` — код остаётся тем же.

## Python

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

resp = client.chat.completions.create(
    model="deepseek-r1:14b",
    messages=[
        {"role": "system", "content": "Отвечай на русском."},
        {"role": "user", "content": "Объясни MoE простыми словами."},
    ],
    temperature=0.6,
)
print(resp.choices[0].message.content)
```

### Стриминг

```python
stream = client.chat.completions.create(
    model="deepseek-r1:14b",
    messages=[{"role": "user", "content": "Напиши хайку про кита."}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

Больше примеров: [examples/](../examples/).

## JavaScript / TypeScript

```js
import OpenAI from "openai";

const client = new OpenAI({ baseURL: "http://localhost:11434/v1", apiKey: "ollama" });

const res = await client.chat.completions.create({
  model: "deepseek-r1:8b",
  messages: [{ role: "user", content: "Привет!" }],
});
console.log(res.choices[0].message.content);
```

## curl

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-r1:8b","messages":[{"role":"user","content":"Привет"}]}'
```

## Структурированный JSON (Ollama native API)

```python
import requests, json

schema = {
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"},
    "skills": {"type": "array", "items": {"type": "string"}}
  },
  "required": ["name", "age", "skills"]
}

r = requests.post("http://localhost:11434/api/chat", json={
    "model": "deepseek-r1:14b",
    "messages": [{"role": "user", "content": "Иван, 29 лет, знает Python и Rust. Верни JSON."}],
    "format": schema,
    "stream": False,
    "think": False,
})
print(json.loads(r.json()["message"]["content"]))
```

## IDE: бесплатный ИИ-помощник для кода

### VS Code + Continue

1. Установи расширение **Continue**.
2. В конфиге добавь модель с провайдером `ollama` и `model: deepseek-r1:14b` (чат) и маленькую модель для автодополнения.

### Cline / Roo Code / Kilo Code

Агенты, которые сами читают и правят файлы. Провайдер **Ollama** или **OpenAI Compatible** → `base_url` локального сервера. Для агентной работы нужна модель с надёжным tool calling и большим контекстом (≥32K): дистилляты 14B+ или V4-Flash.

### Терминальные агенты

Официальный API DeepSeek поддерживает формат Anthropic — по заявлению DeepSeek, V4 работает с Claude Code, OpenCode и подобными CLI-агентами через смену `base_url`. Для полностью локального варианта используй OpenCode/Aider с OpenAI-совместимым бэкендом.

## Официальный API DeepSeek (когда локально не тянет)

```python
client = OpenAI(base_url="https://api.deepseek.com", api_key="sk-...")
client.chat.completions.create(model="deepseek-v4-flash", messages=[...])
```

Модели: `deepseek-v4-flash`, `deepseek-v4-pro`. Старые имена `deepseek-chat` / `deepseek-reasoner` выведены из эксплуатации (по объявлению DeepSeek — 24 июля 2026). Цены и названия — на [api-docs.deepseek.com](https://api-docs.deepseek.com).

[Урок 8: Промптинг →](08-promptting.md)
