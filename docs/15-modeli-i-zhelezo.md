# Урок 15. Все модели DeepSeek 2026: версии, разновидности и железо под каждую

[← Урок 14](14-ustanovka-po-os.md) · [Оглавление](../README.md)

> Актуально на **17 октября 2026**. Последняя модель — **DeepSeek-V4.1-Flash-1017** (вышла 17.10.2026). DeepSeek выпускает обновлённые чекпойнты каждые 1–2 месяца, поэтому названия сверяй в [коллекции deepseek-ai](https://huggingface.co/deepseek-ai).

## 🆕 Что нового (октябрь 2026)

- **DeepSeek-V4.1-Flash-1017.** Обновлённый чекпойнт V4.1-Flash: дообучен через RL с самообратной связью на сквозных проектных задачах. По данным DeepSeek он лучше прошлой версии на всех 11 бенчмарках (DeepSWE v1.1: 74.2 → 77.0, Terminal-Bench 4.0: 31.2 → 42.3), решает задачи быстрее и пишет короче. Веса под MIT: [huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017).
- **Search API и Fetch API.** Официальный веб-поиск и загрузка страниц для агентов и RAG: [api-docs.deepseek.com/guides/search](https://api-docs.deepseek.com/guides/search) (подробнее ниже).
- **deepseek-recipe.** Официальная библиотека на Rust с привязками к Python. Она превращает запросы в форматах Messages, Chat Completions и Responses в промпт V4/V4.1 и разбирает ответ: рассуждения, tool calls, изображения. Нужна при самостоятельном инференсе, потому что Jinja-шаблона в репозитории модели нет.

## 🗂 Полный каталог моделей

### Поколение V4.1 (сентябрь–октябрь 2026), самое новое

| Модель | Параметры | Активных | Контекст / вывод | Модальности | Формат весов |
|---|---|---|---|---|---|
| **DeepSeek-V4.1-Flash-1017** ⭐ | ~552B основа + ~196B Engram-таблиц (HF указывает ~763B) | 8B (prefill) / 16B (decode) | 1M / до 384K | текст + изображения → текст | FP8, ~510 ГБ |
| DeepSeek-V4.1-Flash (сентябрь) | то же | то же | 1M / 384K | текст + изображения | FP8 |

**Чем V4.1 отличается от V4:**

- **Каузальный encoder-decoder.** 40 слоёв: 20 в энкодере и 20 в декодере. Глобальный KV декодера строится из выхода энкодера, поэтому вычислений на префилл почти вдвое меньше.
- **Engram.** Отдельные таблицы памяти (~190 ГБ), которые можно держать на SSD и читать с диска.
- **Сверхкомпактный KV-кэш:** ~890 байт на токен (FP4), примерно в 4 раза меньше V4-Flash. Persistent KV на SSD меньше в ~8 раз.
- **Нативный ввод изображений.**
- **Reasoning effort задаётся числом от 1 до 100.** Уровни API `low`, `high` и `max` соответствуют 50, 75 и 100.

### Поколение V4 (апрель–август 2026)

| Модель | Параметры | Активных | Контекст | Особенности |
|---|---|---|---|---|
| **DeepSeek-V4-Pro-0813** | 1.6T | 49B | 1M | Флагман V4, чекпойнт от 13 августа |
| **DeepSeek-V4-Flash-0731** | 284B | 13B | 1M | Лучший выбор для **домашнего** запуска V4: зрелые GGUF и спекулятивное декодирование DSpark |
| DeepSeek-V4-Flash-Vision-Exp | 284B | 13B | 1M | Экспериментальный вариант с картинками |
| DeepSeek-V4-Pro / V4-Flash (Preview) | 1.6T / 284B | 49B / 13B | 1M | Первые версии от 24 апреля 2026 |

### Предыдущие поколения (всё ещё полезны)

| Модель | Параметры | Зачем сейчас |
|---|---|---|
| DeepSeek-V3.2 / V3.1 | 671B / 37B | Хорошо поддерживаются всеми движками |
| DeepSeek-R1-0528 | 671B / 37B | Классическая reasoning-модель |
| **DeepSeek-R1-0528-Qwen3-8B** | 8B | Лучший дистиллят 8B для ПК |
| DeepSeek-R1-Distill-Qwen 1.5B / 7B / 14B / 32B | 1.5–32B | Ollama `deepseek-r1:*` |
| DeepSeek-R1-Distill-Llama 8B / 70B | 8B / 70B | Ollama `deepseek-r1:8b`, `:70b` |
| DeepSeek-Coder-V2 / -Lite | 236B / 16B | Устаревший, но лёгкий кодер (Lite) |

## 🖥 Какую модель под какое железо

| Железо | Память | Лучший выбор | Как запускать |
|---|---|---|---|
| Ноутбук без GPU | 8–16 ГБ RAM | R1-Distill 1.5B / R1-0528-Qwen3-8B (Q4) | Ollama, LM Studio |
| GPU 8 ГБ (RTX 3060 Ti / 4060) | 8 ГБ VRAM | **R1-0528-Qwen3-8B Q4_K_M** | Ollama, LM Studio |
| GPU 12–16 ГБ (3060 12G, 4060 Ti 16G, 4070 Ti S) | 12–16 ГБ | R1-Distill-Qwen-14B Q4–Q5 | Ollama, LM Studio |
| GPU 24–32 ГБ (3090, 4090, 5090) | 24–32 ГБ | R1-Distill-Qwen-32B Q4 | Ollama, llama.cpp |
| 2× GPU 24 ГБ / Mac 64 ГБ | 48–64 ГБ | R1-Distill-Llama-70B Q4 | llama.cpp, Ollama |
| Mac 96–128 ГБ / DGX Spark / ПК 128 ГБ RAM + GPU 24 ГБ | 96–128 ГБ | **V4-Flash-0731** UD-IQ3_XXS или Q2 | llama.cpp (`-ot` для экспертов), ds4 на Mac |
| Mac Studio 192–256 ГБ | 192–256 ГБ | V4-Flash-0731 Q4–Q8; **V4.1-Flash** в 2 битах (MLX, сообщество) | llama.cpp; MLX-порт |
| Два Mac/Spark по 128 ГБ (TB5/RDMA) | 2×128 ГБ | V4.1-Flash Q2 с тензорным параллелизмом | Кластер (exo и подобные) |
| Mac Studio 512 ГБ | 512 ГБ | V4.1-Flash 4/8-бит (впритык) | MLX |
| 8× H100/H200 80+ ГБ | 640+ ГБ | **V4.1-Flash-1017 FP8** | SGLang, vLLM |
| 8× B200 / GB300 | 1.4+ ТБ | **V4-Pro-0813** (FP8 / NVFP4) | SGLang, vLLM |
| Нет железа | — | V4.1-Flash через облако | API DeepSeek, Ollama Cloud, OpenRouter |

> 💡 **Главное правило 2026 года.** Для дома лучший компромисс — **V4-Flash-0731**. Для неё есть зрелые GGUF, поддержка в llama.cpp и DSpark, и она влезает в 110–170 ГБ. **V4.1-Flash** сильнее, но весит в 2–3 раза больше, и локально её пока поддерживают только SGLang/vLLM на серверах и экспериментальные MLX-порты.

## 🚀 Как запустить DeepSeek-V4.1-Flash-1017

### Сервер с GPU (официальный путь)

**SGLang:**

```bash
pip install -U sglang
python3 -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V4.1-Flash-1017 \
  --host 0.0.0.0 --port 30000
```

**SGLang в Docker:**

```bash
docker run --gpus all --shm-size 32g -p 30000:30000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  lmsysorg/sglang:latest \
  python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-V4.1-Flash-1017 \
  --host 0.0.0.0 --port 30000
```

**vLLM:**

```bash
pip install -U vllm
vllm serve deepseek-ai/DeepSeek-V4.1-Flash-1017
```

> ⚠️ Архитектура `deepseek_v41` новая. Её поддержка в стабильных релизах SGLang и vLLM появляется постепенно, поэтому может понадобиться dev-образ или ветка с PR. Добавь флаги параллелизма под своё железо (`--tp 8` / `--tensor-parallel-size 8`).

**Рекомендуемые параметры (из карточки модели):** `temperature=1.0`, `top_p=1.0`, `max_tokens` от 256K, контекст 1M.

**Шаблон чата.** Jinja-шаблона в репозитории нет. Для своего бэкенда используй `encoding/encoding.py` из репозитория модели или библиотеку **deepseek-recipe**.

### Mac (экспериментально)

- **MLX-порты сообщества**: 2-битная версия занимает ~167 ГБ в памяти (~239 ГБ на диске) и работает на Mac Studio 256 ГБ. Автор замера сообщает ~9.5 ток/с. Смешанные 4/8 бит требуют ~430 ГБ.
- **ds4** (движок Сальваторе Санфилиппо, автора Redis) — нативный Metal-движок, но он для **V4-Flash**, а не для V4.1. Нужны его собственные GGUF: q2 для 128 ГБ, q4 для 256 ГБ+. Статус — alpha.

### llama.cpp / Ollama / LM Studio

На 17.10.2026 архитектура `deepseek_v41` в основной ветке llama.cpp **не поддерживается**. GGUF-файлы V4.1 на Hugging Face выложены сообществом и требуют форков. Пока для локального запуска на ПК выбирай **V4-Flash-0731** ([урок 4](04-llama-cpp.md)).

### Облако, если железа нет

| Где | Модель |
|---|---|
| API DeepSeek | `deepseek-flash` (сейчас ведёт на V4.1-Flash) и `deepseek-v4-pro` |
| Ollama Cloud | `deepseek-v4.1-flash` (облачный, через `ollama signin`) |
| OpenRouter | `deepseek/deepseek-v4.1-flash-1017` |

> Имена и цены в API меняются, поэтому сверяйся с [api-docs.deepseek.com](https://api-docs.deepseek.com).

## 🔎 DeepSeek Search API и Fetch API

Два простых JSON-API для агентов и RAG: **Search** ищет страницы в вебе, **Fetch** скачивает страницу и возвращает её в Markdown. Авторизация та же, что у обычного API DeepSeek.

| | Search | Fetch |
|---|---|---|
| Эндпоинт | `POST https://api.deepseek.com/v1/tools/search` | `POST https://api.deepseek.com/v1/tools/fetch` |
| Цена | $0.75 за 1000 успешных запросов | $0.75 за 1000 успешных запросов |
| Лимит | 5 запросов/с на аккаунт | 5 запросов/с на аккаунт + лимит на домен |

Платишь только за успешные ответы (HTTP 200 с результатом), а пустые выдачи и ошибки бесплатны. Параметр `count` на цену не влияет.

### Параметры Search

| Поле | Тип | По умолчанию | Описание |
|---|---|---|---|
| `query` | string (1–128 символов) | — | Запрос, поддерживает операторы |
| `count` | int 1–50 | 10 | Количество результатов |
| `ori_question` | string | — | Исходный вопрос пользователя, улучшает понимание |
| `localization` | string | `""` | IP-адрес для локализации выдачи |
| `need_content` | bool | false | Вернуть полный текст страниц в `content` |

**Операторы запроса:** `site:github.com`, `-site:`, `-слово`, `"точная фраза"`, `-"фраза"`, `lang:ru,en`, `after:2026-01-01`, `before:...`. Их можно комбинировать, а для нескольких сайтов использовать `OR`.

**Поля ответа (`results[]`):** `title`, `url`, `snippet` (100–200 символов), `summary` (600–800 символов, удобно подавать модели), `content`, `site_name`, `date`, `rerank_score` (0–3, хорошо от 1.5), `authority` (0–4, авторитетно от 3).

### Пример: поиск в Python

```python
import os, requests

H = {"Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}"}

r = requests.post("https://api.deepseek.com/v1/tools/search", headers=H, json={
    "query": "DeepSeek V4.1 llama.cpp lang:ru,en after:2026-09-01",
    "count": 5,
    "ori_question": "Можно ли запустить DeepSeek V4.1 в llama.cpp?",
})
r.raise_for_status()
for x in r.json()["results"]:
    print(f'{x["rerank_score"]:.2f}  {x["title"]}\n      {x["url"]}')
```

### Пример: Fetch

```python
page = requests.post("https://api.deepseek.com/v1/tools/fetch", headers=H,
                     json={"url": "https://github.com/ggml-org/llama.cpp"}).json()
print(page["title"]); print(page["content"][:1000])
```

### 💡 Фишка: веб-поиск для ЛОКАЛЬНОЙ модели

Search API можно подключить как инструмент к локальному DeepSeek в Ollama. Модель работает у тебя, а свежие данные берутся из поиска DeepSeek. Готовый скрипт: [examples/web_search_agent.py](../examples/web_search_agent.py).

### Ошибки

| Код | Что делать |
|---|---|
| 400 / 413 | Исправь запрос |
| 401 | Проверь API-ключ |
| 402 | Пополни баланс |
| 403 / 404 (Fetch) | Сайт запрещает загрузку или пуст, возьми другой URL |
| 408 / 429 / 5xx | Подожди и повтори (экспоненциальная задержка) |

[← К оглавлению](../README.md)
