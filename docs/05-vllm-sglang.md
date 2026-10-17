# Урок 5. vLLM и SGLang: DeepSeek на сервере под нагрузку

[← Урок 4](04-llama-cpp.md) · [Оглавление](../README.md) · [Урок 6 →](06-interfeisy.md)

Ollama и llama.cpp отлично работают для одного пользователя. Когда нужно обслуживать команду или сервис — нужны движки с **continuous batching** и **PagedAttention**: vLLM и SGLang.

## Когда это нужно

- 5+ одновременных пользователей
- Несколько GPU в одной машине или кластере
- Нужна максимальная пропускная способность (токенов/с суммарно)
- Запуск V4-Pro или V4-Flash в «родной» точности (FP8/FP4)

## vLLM

### Установка

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U vllm
```

Или Docker:

```bash
docker run --gpus all -p 8000:8000 --ipc=host \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --max-model-len 32768
```

### Дистиллят на 1–2 GPU

```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --tensor-parallel-size 2 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.92 \
  --reasoning-parser deepseek_r1
```

`--reasoning-parser` выносит рассуждения в поле `reasoning_content`, а `content` содержит чистый ответ.

### V4 на мульти-GPU

```bash
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 8 \
  --max-model-len 131072 \
  --trust-remote-code
```

> ⚠️ Поддержка V4 в vLLM зависит от версии и GPU (на момент написания основная ветка ориентирована на Hopper/Blackwell; для Ampere существуют community-форки). Смотри карточку модели и [рецепты vLLM](https://docs.vllm.ai/projects/recipes/).

## SGLang

SGLang исторически лучше всех оптимизирован под архитектуру DeepSeek (MLA, MoE, DP-attention).

```bash
pip install -U "sglang[all]"

python3 -m sglang.launch_server \
  --model-path deepseek-ai/DeepSeek-V4-Flash \
  --tp 8 --trust-remote-code \
  --host 0.0.0.0 --port 30000
```

Для V4-Pro на Blackwell существуют NVFP4-чекпойнты от NVIDIA — они вдвое уменьшают память по сравнению с FP8.

## Ключевые параметры производительности

| Параметр | vLLM | SGLang | Совет |
|---|---|---|---|
| Тензорный параллелизм | `--tensor-parallel-size` | `--tp` | = число GPU в узле |
| Экспертный параллелизм | `--enable-expert-parallel` | `--ep` / `--enable-ep-moe` | Для MoE на многих GPU |
| Макс. контекст | `--max-model-len` | `--context-length` | Не ставь больше нужного — экономит KV-кэш |
| Доля VRAM | `--gpu-memory-utilization` | `--mem-fraction-static` | 0.85–0.93 |
| FP8 KV-кэш | `--kv-cache-dtype fp8` | `--kv-cache-dtype fp8_e5m2` | ×2 к вместимости контекста |
| Кэш префиксов | включён по умолчанию | RadixAttention (по умолчанию) | Ускоряет общий системный промпт |

## Тест нагрузки

```bash
vllm bench serve --model deepseek-ai/DeepSeek-R1-Distill-Qwen-32B \
  --dataset-name random --random-input-len 1024 --random-output-len 512 \
  --num-prompts 200 --request-rate 10
```

Смотри на **TTFT** (время до первого токена) и **TPOT** (время на токен) — это то, что видят пользователи.

## Что выбрать

| Ситуация | Выбор |
|---|---|
| Один GPU, несколько пользователей, дистиллят | vLLM |
| Большой MoE DeepSeek на 8 GPU | SGLang (или vLLM — сравни на своём железе) |
| Нет NVIDIA / смешанное CPU+GPU | llama.cpp `llama-server` с `-np` |

[Урок 6: Интерфейсы →](06-interfeisy.md)
