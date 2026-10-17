# Урок 4. llama.cpp: запуск DeepSeek V4-Flash и тонкая настройка

[← Урок 3](03-ollama.md) · [Оглавление](../README.md) · [Урок 5 →](05-vllm-sglang.md)

llama.cpp — движок, на котором построены Ollama и LM Studio. Он первым получает поддержку новых архитектур и даёт полный контроль: какие слои на GPU, какие эксперты в RAM, как кэшировать контекст.

## Сборка

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake curl libcurl4-openssl-dev pciutils git
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp

# NVIDIA
cmake -B build -DGGML_CUDA=ON
# Apple Silicon (Metal включён по умолчанию)
cmake -B build
# AMD / Intel / любая GPU через Vulkan
cmake -B build -DGGML_VULKAN=ON
# только CPU
cmake -B build -DGGML_CUDA=OFF

cmake --build build --config Release -j
```

Бинарники появятся в `build/bin/`: `llama-cli`, `llama-server`, `llama-bench`, `llama-gguf-split`.

> 💡 Готовые сборки под Windows/macOS есть в [Releases](https://github.com/ggml-org/llama.cpp/releases), а на macOS — `brew install llama.cpp`.

## Запуск дистиллята (простой случай)

```bash
./build/bin/llama-cli \
  -hf unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M \
  -ngl 99 -c 16384 --temp 0.6 --top-p 0.95
```

## Запуск DeepSeek-V4-Flash (284B)

### 1. Скачать квант

```bash
pip install -U huggingface_hub
hf download unsloth/DeepSeek-V4-Flash-0731-GGUF \
  --local-dir models/V4-Flash \
  --include "*UD-IQ3_XXS*"      # ~103 ГБ; "*UD-Q4_K_XL*" — ~155 ГБ
```

> Названия репозиториев и чекпойнтов меняются — смотри актуальные на [странице Unsloth](https://unsloth.ai/docs/models/deepseek-v4) и в [коллекции deepseek-ai](https://huggingface.co/deepseek-ai).

### 2. Mac Studio / DGX Spark (вся модель в единой памяти)

```bash
./build/bin/llama-cli \
  --model models/V4-Flash/UD-IQ3_XXS/DeepSeek-V4-Flash-0731-UD-IQ3_XXS-00001-of-00004.gguf \
  -ngl 99 -c 32768 \
  --temp 1.0 --top-p 1.0 --min-p 0.01
```

Указываешь **первый** файл из частей — остальные подхватятся сами.

### 3. ПК: одна GPU 24 ГБ + 128+ ГБ RAM (оффлоад экспертов) 🔥

```bash
./build/bin/llama-server \
  --model models/V4-Flash/UD-IQ3_XXS/DeepSeek-V4-Flash-0731-UD-IQ3_XXS-00001-of-00004.gguf \
  -ngl 99 \
  -ot ".ffn_.*_exps.=CPU" \
  -c 32768 --threads 16 \
  --temp 1.0 --top-p 1.0 --min-p 0.01 \
  --host 0.0.0.0 --port 8080
```

**Как это работает:** `-ngl 99` отправляет все слои на GPU, а `-ot` (override-tensor) возвращает тяжёлые тензоры экспертов MoE в оперативную память. На GPU остаются внимание и общие слои — то, что считается на каждом токене. Если VRAM остаётся свободной, верни часть экспертов на GPU, например:

```bash
-ot "blk\.(1[0-9]|[0-9])\.ffn_.*_exps.=CUDA0" -ot ".ffn_.*_exps.=CPU"
```

## Режимы размышлений V4

```bash
--reasoning off                                        # без размышлений
--chat-template-kwargs '{"enable_thinking":false}'    # то же через шаблон
--chat-template-kwargs '{"reasoning_effort":"max"}'   # максимальные размышления
```

Windows PowerShell: `--chat-template-kwargs "{\"enable_thinking\":false}"`.

## Спекулятивное декодирование (DSpark)

Unsloth публикует для V4-Flash маленький «драфтер», который угадывает несколько токенов вперёд, а большая модель их проверяет:

```bash
./build/bin/llama-cli \
  --model models/V4-Flash/UD-IQ3_XXS/...-00001-of-00004.gguf \
  -md models/V4-Flash/dspark-DeepSeek-V4-Flash-0731-Q8_0.gguf \
  --spec-type draft-dspark --spec-draft-n-max 3 \
  -ngl 99 -ngld 99 \
  --temp 1.0 --top-p 1.0 --min-p 0.01
```

По данным Unsloth — ~1.5–2× ускорение генерации ценой ~10 ГБ памяти. `--spec-draft-n-max 3` — оптимум, большие значения медленнее.

## llama-server: OpenAI-совместимый API + веб-чат

`llama-server` поднимает:

- веб-интерфейс на `http://localhost:8080`
- API `http://localhost:8080/v1/chat/completions`

Полезные флаги сервера:

| Флаг | Что делает |
|---|---|
| `-c 65536` | Размер контекста |
| `-np 4` | Параллельные слоты (контекст делится между ними) |
| `--cache-type-k q8_0 --cache-type-v q8_0` | Квантованный KV-кэш |
| `-fa on` | Flash-attention |
| `--jinja` | Использовать Jinja-шаблон чата из GGUF (нужно для tool calling) |
| `--api-key secret` | Простая авторизация |
| `--mlock` | Запретить выгрузку модели в своп |
| `--no-mmap` | Загрузить целиком в RAM (иногда быстрее на Windows) |

## Справочник ключевых флагов

| Флаг | Смысл |
|---|---|
| `-m / --model` | Путь к GGUF |
| `-hf repo:quant` | Скачать с Hugging Face автоматически |
| `-ngl N` | Сколько слоёв на GPU (99 = все) |
| `-ot regex=устройство` | Куда положить тензоры (CPU, CUDA0, …) |
| `-c N` | Контекст |
| `-t N` | Потоки CPU (= физические ядра) |
| `-b / -ub` | Размер батча обработки промпта (больше — быстрее префилл, больше памяти) |
| `--temp / --top-p / --min-p` | Сэмплинг |
| `-md`, `-ngld` | Модель-драфтер и её слои на GPU |

## Замер скорости

```bash
./build/bin/llama-bench -m model.gguf -ngl 99 -p 512 -n 128
```

`pp` — скорость обработки промпта, `tg` — скорость генерации (то, что ты «чувствуешь»).

[Урок 5: vLLM и SGLang →](05-vllm-sglang.md)
