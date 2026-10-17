# Урок 3. Ollama + DeepSeek: от первого запуска до тонкой настройки

[← Урок 2](02-zhelezo.md) · [Оглавление](../README.md) · [Урок 4 →](04-llama-cpp.md)

## Установка

| ОС | Команда |
|---|---|
| Windows | Установщик с [ollama.com/download](https://ollama.com/download) |
| macOS | Установщик или `brew install ollama` |
| Linux | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Docker | `docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama` |

Проверка: `ollama --version`.

## Базовые команды

```bash
ollama pull deepseek-r1:14b   # скачать
ollama run deepseek-r1:14b    # чат в терминале
ollama list                   # установленные модели
ollama ps                     # что сейчас в памяти и на чём
ollama stop deepseek-r1:14b   # выгрузить из памяти
ollama rm deepseek-r1:14b     # удалить
ollama show deepseek-r1:14b   # параметры, шаблон, лицензия
```

## Модели DeepSeek в библиотеке Ollama

- `deepseek-r1:1.5b`, `7b`, `8b`, `14b`, `32b`, `70b` — дистилляты (локально)
- `deepseek-r1:671b` — полная R1 (нужно ~400+ ГБ)
- `deepseek-v3`, `deepseek-v3.1`, `deepseek-coder-v2` — предыдущие поколения
- `deepseek-v4-flash:cloud`, `deepseek-v4-pro:cloud` — **облачные** теги: работают через серверы ollama.com (нужен `ollama signin`), веса не скачиваются

> Теги меняются — сверяйся с [ollama.com/library](https://ollama.com/search?q=deepseek).

## Команды внутри чата

```
/set parameter num_ctx 16384     # контекст
/set parameter temperature 0.6
/set system "Отвечай только на русском языке."
/set think                       # включить размышления (для моделей, которые умеют)
/set nothink                     # выключить
/save my-deepseek                # сохранить как новую модель
/bye
```

## Modelfile: своя «сборка» модели

Файл `Modelfile` (готовый пример — [configs/Modelfile.ru-assistant](../configs/Modelfile.ru-assistant)):

```dockerfile
FROM deepseek-r1:14b

PARAMETER num_ctx 16384
PARAMETER temperature 0.6
PARAMETER top_p 0.95
PARAMETER repeat_penalty 1.05
PARAMETER num_predict 4096

SYSTEM """Ты — полезный ассистент. Всегда отвечай на русском языке, кратко и по делу."""
```

```bash
ollama create ds-ru -f Modelfile
ollama run ds-ru
```

## Подключение любого GGUF с Hugging Face

```bash
# прямо из HF (одиночный GGUF-файл)
ollama run hf.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M
```

Или локальный файл:

```dockerfile
FROM ./model-Q4_K_M.gguf
```

> ⚠️ Многочастные (sharded) GGUF, как у V4-Flash, Ollama может не принять — для них используй llama.cpp ([урок 4](04-llama-cpp.md)).

## Переменные окружения — главные фишки

| Переменная | Значение | Эффект |
|---|---|---|
| `OLLAMA_CONTEXT_LENGTH` | `32768` | Контекст по умолчанию для всех моделей |
| `OLLAMA_FLASH_ATTENTION` | `1` | Flash-attention: меньше памяти, быстрее |
| `OLLAMA_KV_CACHE_TYPE` | `q8_0` | Сжатый KV-кэш (требует flash-attention) |
| `OLLAMA_KEEP_ALIVE` | `-1` / `24h` | Не выгружать модель |
| `OLLAMA_NUM_PARALLEL` | `4` | Параллельные запросы к одной модели |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | Сколько моделей держать одновременно |
| `OLLAMA_HOST` | `0.0.0.0:11434` | Доступ из локальной сети |
| `OLLAMA_MODELS` | `/data/models` | Перенести модели на другой диск |

**Как задать:**

- **Linux (systemd):** `sudo systemctl edit ollama` →
  ```ini
  [Service]
  Environment="OLLAMA_FLASH_ATTENTION=1"
  Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
  Environment="OLLAMA_CONTEXT_LENGTH=32768"
  ```
  затем `sudo systemctl daemon-reload && sudo systemctl restart ollama`.
- **macOS:** `launchctl setenv OLLAMA_FLASH_ATTENTION 1` и перезапуск приложения.
- **Windows:** «Изменение переменных среды» → добавить → перезапустить Ollama из трея.

## Размышления в API

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "deepseek-r1:8b",
  "messages": [{"role": "user", "content": "Сколько будет 17*23?"}],
  "think": true,
  "stream": false
}'
```

В ответе рассуждение придёт отдельно в `message.thinking`, ответ — в `message.content`. `"think": false` — модель ответит сразу (где поддерживается).

## Чек-лист «Ollama настроен правильно»

- [ ] `ollama ps` показывает `100% GPU`
- [ ] Контекст увеличен под задачу
- [ ] Включены flash-attention и KV-кэш q8_0
- [ ] Температура 0.5–0.7 для R1
- [ ] Модель не выгружается между запросами

[Урок 4: llama.cpp →](04-llama-cpp.md)
