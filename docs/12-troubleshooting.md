# Урок 12. Траблшутинг: ошибки при запуске DeepSeek и их решения

[← Урок 11](11-prod-i-bezopasnost.md) · [Оглавление](../README.md)

## Память

### `CUDA error: out of memory` / `failed to allocate`

1. Уменьши контекст: `num_ctx` / `-c`.
2. Включи квантованный KV-кэш (`q8_0`) и flash-attention.
3. Возьми квант меньше (Q4_K_M → Q3_K_M).
4. Отправь часть слоёв на CPU: `-ngl 30` вместо 99, или эксперты MoE через `-ot`.
5. Закрой браузер/игры — они тоже занимают VRAM.

### Система зависает, всё в свопе

Модель больше RAM. Возьми меньшую модель или квант. На Linux проверь `free -h`; включи `--mlock` только если памяти точно хватает.

## Скорость

### 1–3 токена в секунду на видеокарте

- `ollama ps` → если не `100% GPU`, модель не влезла.
- Проверь, что Ollama видит GPU: в логах должно быть упоминание CUDA/ROCm/Metal.
- Windows: обнови драйвер NVIDIA. Linux: `nvidia-smi` должен работать.
- AMD: проверь поддержку ROCm для своей карты или используй Vulkan-сборку.

### Первый ответ ждать очень долго

Модель загружается в память. Поставь `OLLAMA_KEEP_ALIVE=-1`. Для огромных моделей — быстрый NVMe-диск.

## Качество

### Модель бесконечно «думает» или повторяется

- Температура 0.6 для R1 (не 0!), 1.0 для V4.
- `repeat_penalty 1.05–1.1`.
- Лимит длины ответа `num_predict`.
- Контекст должен вмещать рассуждение + ответ — увеличь `num_ctx`.

### Отвечает на английском/китайском

- Системный промпт + повтор инструкции в сообщении пользователя: «Ответь на русском».
- Дистилляты 1.5B–8B плохо держат русский — переходи на 14B+.

### Ответ обрывается

`num_predict` / `max_tokens` слишком мал, или переполнен контекст.

### `<think>` виден в ответе / не виден вообще

- В Ollama: обнови до свежей версии — рассуждения идут в отдельное поле `thinking`.
- В llama.cpp: используй `--jinja` и правильный шаблон; `--reasoning-format deepseek` выносит рассуждения в `reasoning_content`.
- В vLLM: `--reasoning-parser deepseek_r1`.

## Загрузка и форматы

### `unknown model architecture`

Твоя версия llama.cpp/Ollama ещё не поддерживает архитектуру (типично для свежих V4-GGUF). Обнови или собери llama.cpp из `master`.

### Ollama не принимает GGUF из нескольких частей

Склей: `llama-gguf-split --merge part-00001-of-0000N.gguf merged.gguf` или запускай через llama.cpp.

### Скачивание с Hugging Face обрывается

```bash
pip install -U "huggingface_hub[hf_transfer]"
HF_HUB_ENABLE_HF_TRANSFER=1 hf download <repo> --include "*Q4_K_M*" --local-dir ./models
```

Повторный запуск докачает файлы. При проблемах с доступом — переменная `HF_ENDPOINT` для зеркала.

## Docker

### Open WebUI не видит Ollama

- URL должен быть `http://host.docker.internal:11434` (не `localhost`, если Open WebUI в контейнере).
- На Linux добавь `--add-host=host.docker.internal:host-gateway`.
- Ollama должна слушать не только 127.0.0.1: `OLLAMA_HOST=0.0.0.0` (и закрой порт файрволом снаружи!).

### Контейнер не видит GPU

Установи NVIDIA Container Toolkit, проверь: `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi`.

---

Не нашёл свою проблему? [Открой Issue](../../../issues) с выводом команды, версией и характеристиками железа.

[← К оглавлению](../README.md)
