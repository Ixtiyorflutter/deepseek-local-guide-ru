<div align="center">

# 🐋 DeepSeek локально — полный курс на русском (2026)

**Как установить, запустить и выжать максимум из DeepSeek V4, R1 и дистиллятов у себя на ПК, Mac и сервере.**
Ollama · llama.cpp · LM Studio · vLLM · SGLang · Open WebUI · API · RAG · агенты · квантизация

[![Stars](https://img.shields.io/github/stars/justxor/deepseek-local-guide-ru?style=social)](https://github.com/justxor/deepseek-local-guide-ru)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
![Language](https://img.shields.io/badge/язык-русский-red)
![Updated](https://img.shields.io/badge/обновлено-октябрь%202026-orange)

⭐ **Поставь звезду, если гайд полезен — так его найдут другие.**

</div>

---

> **Кратко:** DeepSeek — семейство открытых (open-weight, лицензия MIT) LLM от китайской лаборатории DeepSeek-AI. Флагманы **DeepSeek-V4-Pro** (1.6T параметров, 49B активных) и **DeepSeek-V4-Flash** (284B, 13B активных) поддерживают контекст **1 млн токенов** и режимы «с размышлением / без». На обычном ПК реально запускать **дистилляты DeepSeek-R1** (1.5B–70B) через Ollama, а **V4-Flash** — на машине со ~110+ ГБ RAM/VRAM через llama.cpp. Этот репозиторий — пошаговый курс от «первого запуска за 5 минут» до продакшн-сервера с API, RAG и агентами.

## 📑 Оглавление

- [Для кого этот курс](#-для-кого-этот-курс)
- [Быстрый старт за 5 минут](#-быстрый-старт-за-5-минут)
- [Какую модель DeepSeek выбрать](#-какую-модель-deepseek-выбрать-под-железо)
- [Программа курса (уроки)](#-программа-курса)
- [Топ-25 фишек и приёмов](#-топ-25-фишек-и-приёмов)
- [Сравнение способов запуска](#-сравнение-способов-запуска)
- [Частые ошибки](#-частые-ошибки-и-решения)
- [FAQ](#-faq)
- [Полезные ссылки](#-полезные-ссылки)

## 🎯 Для кого этот курс

| Ты… | Начни с |
|---|---|
| Новичок, хочешь «ChatGPT у себя без интернета» | [Урок 1](docs/01-vvedenie.md) → [Урок 3 (Ollama)](docs/03-ollama.md) → [Урок 6 (Open WebUI)](docs/06-interfeisy.md) |
| Разработчик, нужен локальный API | [Урок 3](docs/03-ollama.md) → [Урок 7 (API)](docs/07-api-i-integracii.md) → [примеры кода](examples/) |
| Энтузиаст, хочешь запустить V4-Flash целиком | [Урок 2 (железо)](docs/02-zhelezo.md) → [Урок 4 (llama.cpp)](docs/04-llama-cpp.md) → [Урок 9 (оптимизация)](docs/09-optimizaciya.md) |
| DevOps / ML-инженер, нужен сервер под команду | [Урок 5 (vLLM/SGLang)](docs/05-vllm-sglang.md) → [Урок 11 (прод)](docs/11-prod-i-bezopasnost.md) |

## ⚡ Быстрый старт за 5 минут

**Windows / macOS:** скачай установщик с [ollama.com/download](https://ollama.com/download).
**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Запусти модель (подбери размер под свою видеопамять — см. таблицу ниже):

```bash
ollama run deepseek-r1:8b
```

Готово — пишешь в терминал, модель отвечает локально, без интернета. Хочешь интерфейс как у ChatGPT:

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

Открой `http://localhost:3000`. Подробно — в [уроке 6](docs/06-interfeisy.md).

## 🧠 Какую модель DeepSeek выбрать под железо

| Модель | Параметры (всего / активных) | Где запускать | Минимум памяти* | Для чего |
|---|---|---|---|---|
| `deepseek-r1:1.5b` | 1.5B | Ollama, LM Studio | 4 ГБ RAM | Слабые ноутбуки, эксперименты |
| `deepseek-r1:7b` / `8b` | 7–8B | Ollama, LM Studio | 6–8 ГБ VRAM | Лучший старт для большинства |
| `deepseek-r1:14b` | 14B | Ollama, LM Studio | 10–12 ГБ VRAM | RTX 3060 12GB / 4070 |
| `deepseek-r1:32b` | 32B | Ollama, llama.cpp | 20–24 ГБ VRAM | RTX 3090 / 4090, Mac 32 ГБ+ |
| `deepseek-r1:70b` | 70B | Ollama, llama.cpp | 40–48 ГБ | 2×24 ГБ, Mac 64 ГБ+ |
| **DeepSeek-V4-Flash** (GGUF) | 284B / 13B (MoE) | llama.cpp | ~110 ГБ (3-бит) | Mac Studio 128–192 ГБ, DGX Spark, ПК с 128 ГБ RAM + GPU |
| **DeepSeek-V4-Pro** | 1.6T / 49B (MoE) | vLLM, SGLang | 8×H200/B200 | Дата-центр |
| V4 через `:cloud` в Ollama | — | Ollama Cloud | любой ПК | Когда железа нет, но нужен интерфейс Ollama |

\* Ориентиры для 4-битной квантизации и короткого контекста. Длинный контекст требует дополнительной памяти под KV-кэш. Подробный расчёт — в [уроке 2](docs/02-zhelezo.md).

> ⚠️ Модели `deepseek-r1:*` в Ollama (кроме 671b) — это **дистилляты**: архитектура Qwen/Llama, дообученная на рассуждениях DeepSeek-R1. Это не «настоящий» DeepSeek, но лучшее, что влезает в домашнюю видеокарту.

## 📚 Программа курса

| # | Урок | Что узнаешь |
|---|---|---|
| 01 | [Введение: что такое DeepSeek](docs/01-vvedenie.md) | История моделей V2→V3→R1→V4, MoE, лицензия, зачем запускать локально |
| 02 | [Железо и расчёт памяти](docs/02-zhelezo.md) | Формулы VRAM, квантизация, MoE-оффлоад, Mac vs NVIDIA vs AMD |
| 03 | [Ollama: от нуля до профи](docs/03-ollama.md) | Установка, Modelfile, контекст, переменные окружения, кастомные GGUF |
| 04 | [llama.cpp: максимум контроля](docs/04-llama-cpp.md) | Сборка с CUDA/Metal/Vulkan, запуск V4-Flash, `llama-server`, флаги |
| 05 | [vLLM и SGLang: сервер под нагрузку](docs/05-vllm-sglang.md) | Тензорный параллелизм, FP8/NVFP4, батчинг, мульти-GPU |
| 06 | [Интерфейсы: Open WebUI, LM Studio, Jan](docs/06-interfeisy.md) | ChatGPT-подобный UI, документы, голос, мультипользователь |
| 07 | [API и интеграции](docs/07-api-i-integracii.md) | OpenAI-совместимый API, Python/JS, VS Code, IDE-агенты |
| 08 | [Промптинг DeepSeek: приёмы](docs/08-promptting.md) | Режим размышлений, `<think>`, температуры, JSON, системные промпты |
| 09 | [Оптимизация скорости](docs/09-optimizaciya.md) | Спекулятивное декодирование, KV-кэш, flash-attention, оффлоад экспертов |
| 10 | [RAG и агенты](docs/10-rag-i-agenty.md) | Чат с документами, tool calling, LangChain/LlamaIndex |
| 11 | [Продакшн и безопасность](docs/11-prod-i-bezopasnost.md) | Docker, nginx, авторизация, мониторинг, приватность |
| 12 | [Траблшутинг](docs/12-troubleshooting.md) | Разбор ошибок OOM, медленной генерации, «зацикливания» |

📂 Также: [готовые примеры кода](examples/) · [конфиги и docker-compose](configs/) · [шпаргалка команд](docs/cheatsheet.md)

## 🔥 Топ-25 фишек и приёмов

<details open>
<summary><b>Запуск и память</b></summary>

1. **Бери Q4_K_M по умолчанию.** Лучший баланс качества и размера; Q5_K_M — если память позволяет, Q8_0 — почти без потерь.
2. **Динамические кванты Unsloth (`UD-*`)** для V4-Flash: важные слои остаются в высокой точности, а 3-битная модель влезает в ~110 ГБ.
3. **Оффлоад экспертов MoE на CPU:** `-ot ".ffn_.*_exps.=CPU"` в llama.cpp — общие слои и внимание на GPU, «эксперты» в RAM. Так 284B-модель работает с одной видеокартой на 24 ГБ.
4. **Увеличь контекст в Ollama явно:** по умолчанию он маленький. `OLLAMA_CONTEXT_LENGTH=32768` или `PARAMETER num_ctx 32768` в Modelfile.
5. **Квантизуй KV-кэш:** `OLLAMA_KV_CACHE_TYPE=q8_0` + `OLLAMA_FLASH_ATTENTION=1` — почти вдвое меньше памяти под длинный контекст.
6. **`OLLAMA_KEEP_ALIVE=-1`** — модель не выгружается из памяти, нет задержки на первый ответ.
7. **На Mac подними лимит видеопамяти:** `sudo sysctl iogpu.wired_limit_mb=<МБ>` (macOS Sonoma+), чтобы GPU мог использовать больше единой памяти.

</details>

<details>
<summary><b>Качество ответов</b></summary>

8. **Для R1-дистиллятов: temperature 0.5–0.7** (рекомендация DeepSeek — 0.6), top_p 0.95. Иначе возможны повторы и бессвязность.
9. **Для V4: temperature 1.0, top_p 1.0** (агентные сценарии — top_p 0.95), рекомендация из гайда Unsloth.
10. **R1: инструкции — в сообщение пользователя, не в системный промпт.** Так советовала сама DeepSeek для серии R1.
11. **Для математики** добавь: «Рассуждай пошагово и помести итоговый ответ в \boxed{}».
12. **Выключай размышления, когда они не нужны:** в llama.cpp — `--reasoning off` или `--chat-template-kwargs '{"enable_thinking":false}'`; в Ollama — `/set nothink` или `"think": false` в API.
13. **Max-режим размышлений V4** (`reasoning_effort: "max"`) — для сложных задач, но требует большого контекста (от 384K по рекомендации Unsloth).
14. **Вырезай `<think>…</think>` из истории диалога**, чтобы не забивать контекст старыми рассуждениями.
15. **Structured output:** Ollama поддерживает `format` с JSON Schema — модель обязана вернуть валидный JSON.

</details>

<details>
<summary><b>Скорость</b></summary>

16. **Спекулятивное декодирование** (DSpark-драфтер для V4-Flash в llama.cpp) — до ~1.5–2× быстрее генерация.
17. **Все слои на GPU** (`-ngl 99`), если влезает. Каждый слой в RAM заметно замедляет.
18. **Потоки = физические ядра**, а не логические: `--threads 16` на 16-ядерном CPU.
19. **`--mlock` / `--no-mmap`** — если система «свопает» модель и скорость скачет.
20. **vLLM/SGLang для параллельных пользователей** — continuous batching даёт кратный прирост пропускной способности по сравнению с Ollama.

</details>

<details>
<summary><b>Интеграции</b></summary>

21. **Любой клиент OpenAI работает с локальной моделью:** `base_url="http://localhost:11434/v1"`, ключ — любая строка.
22. **Continue / Cline / Roo Code в VS Code** + локальный DeepSeek = бесплатный приватный ИИ-ассистент для кода.
23. **Open WebUI + документы** = RAG «из коробки» без строчки кода.
24. **Официальный API DeepSeek совместим с форматами OpenAI и Anthropic** — можно переключаться между облаком и локалкой, меняя только `base_url`.
25. **Один `docker compose up`** поднимает Ollama + Open WebUI — см. [configs/docker-compose.yml](configs/docker-compose.yml).

</details>

## ⚖️ Сравнение способов запуска

| Инструмент | Сложность | Скорость | Мульти-юзер | GUI | Лучше всего для |
|---|---|---|---|---|---|
| **Ollama** | ⭐ | ★★★ | ★★ | нет (CLI/API) | Старт, разработка, большинство задач |
| **LM Studio** | ⭐ | ★★★ | ★ | да | Новички на Windows/Mac, выбор квантов мышкой |
| **llama.cpp** | ⭐⭐⭐ | ★★★★ | ★★ | веб-UI в `llama-server` | Тонкая настройка, огромные MoE на гибриде CPU+GPU |
| **vLLM** | ⭐⭐⭐⭐ | ★★★★★ | ★★★★★ | нет | Продакшн, много GPU, высокая нагрузка |
| **SGLang** | ⭐⭐⭐⭐ | ★★★★★ | ★★★★★ | нет | Продакшн DeepSeek V3/V4, MLA-оптимизации |
| **Open WebUI** | ⭐⭐ | — (фронтенд) | ★★★★ | да | Командный «ChatGPT» поверх любого бэкенда |

## 🛠 Частые ошибки и решения

| Симптом | Причина | Решение |
|---|---|---|
| `CUDA out of memory` | Модель/контекст не влезают | Меньше квант, меньше `num_ctx`, часть слоёв на CPU |
| 1–2 токена/с | Модель ушла в RAM/своп | Проверь `ollama ps` — должно быть `100% GPU` |
| Бесконечные рассуждения | Слишком низкая/высокая температура | 0.6 для R1, лимит `num_predict` |
| Модель «забывает» начало | Маленький контекст по умолчанию | Увеличь `num_ctx` |
| Ответы на китайском/английском | Дистиллят «съезжает» с языка | Системный промпт «Отвечай только на русском» + пример ответа |

Полный разбор — [урок 12](docs/12-troubleshooting.md).

## ❓ FAQ

<details>
<summary><b>Можно ли запустить DeepSeek без видеокарты?</b></summary>
Да. Ollama и llama.cpp работают на CPU. Модели 1.5B–8B дадут 5–15 токенов/с на современном процессоре. Для V4-Flash нужно 128+ ГБ RAM и терпение.
</details>

<details>
<summary><b>Безопасно ли запускать DeepSeek локально? Данные уходят в Китай?</b></summary>
Нет. Локальная модель — это файл с весами; он не отправляет данные по сети. Сетевые запросы делает только программа-запускатель (при скачивании модели). Для параноидального режима — запускай без интернета после загрузки. Облачные теги `:cloud` и chat.deepseek.com — это уже не локальный запуск.
</details>

<details>
<summary><b>Можно ли использовать DeepSeek в коммерческих проектах?</b></summary>
Веса V3/R1/V4 опубликованы под лицензией MIT — коммерческое использование разрешено. Дистилляты наследуют лицензию базовой модели (Qwen — Apache 2.0, Llama — Llama Community License). Всегда проверяй карточку модели на Hugging Face. Это не юридическая консультация.
</details>

<details>
<summary><b>Что лучше: DeepSeek R1 или V4?</b></summary>
V4 — более новое поколение с гибридным режимом (думает или отвечает сразу) и контекстом 1M. Но для домашнего ПК реалистичны только дистилляты R1 — V4-Flash требует ~110+ ГБ памяти.
</details>

<details>
<summary><b>Чем Ollama отличается от llama.cpp?</b></summary>
Ollama — удобная обёртка над движком на базе llama.cpp: каталог моделей, автозагрузка, API. llama.cpp даёт больше ручных настроек и раньше получает поддержку новых архитектур (например, V4-Flash GGUF).
</details>

## 🔗 Полезные ссылки

- [DeepSeek на Hugging Face](https://huggingface.co/deepseek-ai) — официальные веса
- [Новость о релизе V4 (API Docs)](https://api-docs.deepseek.com/news/news260424/)
- [Ollama: библиотека моделей](https://ollama.com/library)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Unsloth: гайд по DeepSeek V4](https://unsloth.ai/docs/models/deepseek-v4)
- [vLLM](https://github.com/vllm-project/vllm) · [SGLang](https://github.com/sgl-project/sglang)
- [Open WebUI](https://github.com/open-webui/open-webui) · [LM Studio](https://lmstudio.ai)

## 🤝 Вклад

Нашёл ошибку, устаревшую команду или знаешь фишку? Открой Issue или PR — см. [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 Лицензия

Тексты — [CC BY 4.0](LICENSE). Код в `examples/` и `configs/` — MIT.
DeepSeek — торговая марка соответствующего владельца; проект неофициальный.

---

<div align="center">

**Ключевые слова:** deepseek локально, как запустить deepseek на пк, deepseek ollama, deepseek r1 установка, deepseek v4 gguf, llama.cpp deepseek, локальная нейросеть, LLM на своём компьютере, deepseek без интернета, open webui, локальный chatgpt, deepseek api, deepseek гайд на русском

⭐ Если курс помог — поставь звезду и поделись с коллегами!

</div>
