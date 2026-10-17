# Шпаргалка: DeepSeek локально — все команды на одной странице

[← К оглавлению](../README.md)

## Ollama

```bash
ollama run deepseek-r1:8b                 # запустить
ollama run deepseek-r1:8b --verbose       # + статистика скорости
ollama ps                                 # что в памяти, GPU/CPU
ollama create ds-ru -f Modelfile          # своя модель
ollama run hf.co/<user>/<repo>:Q4_K_M     # GGUF с Hugging Face
ollama signin && ollama run deepseek-v4-flash:cloud   # V4 в облаке Ollama
```

Внутри чата: `/set parameter num_ctx 32768` · `/set think` · `/set nothink` · `/save имя` · `/bye`

Переменные: `OLLAMA_FLASH_ATTENTION=1` · `OLLAMA_KV_CACHE_TYPE=q8_0` · `OLLAMA_CONTEXT_LENGTH=32768` · `OLLAMA_KEEP_ALIVE=-1` · `OLLAMA_HOST=0.0.0.0`

## llama.cpp

```bash
cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j

llama-cli -hf <repo>:<quant> -ngl 99 -c 16384 --temp 0.6 --top-p 0.95

# MoE (V4-Flash): эксперты в RAM, остальное на GPU
llama-server -m model-00001-of-0000N.gguf -ngl 99 -ot ".ffn_.*_exps.=CPU" \
  -c 32768 -fa on --cache-type-k q8_0 --cache-type-v q8_0 --jinja --port 8080

--reasoning off                                   # без размышлений
--chat-template-kwargs '{"reasoning_effort":"max"}'

llama-bench -m model.gguf -ngl 99                 # замер скорости
llama-gguf-split --merge in-00001-of-00004.gguf out.gguf
```

## Скачивание

```bash
hf download <repo> --include "*Q4_K_M*" --local-dir ./models
```

## vLLM / SGLang

```bash
vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-32B --tensor-parallel-size 2 \
  --max-model-len 32768 --reasoning-parser deepseek_r1

python3 -m sglang.launch_server --model-path deepseek-ai/DeepSeek-V4-Flash --tp 8 --trust-remote-code
```

## Порты по умолчанию

| Ollama | llama-server | LM Studio | vLLM | SGLang | Open WebUI |
|---|---|---|---|---|---|
| 11434 | 8080 | 1234 | 8000 | 30000 | 3000 (в примерах) |

## Сэмплинг

| Модель | temp | top_p |
|---|---|---|
| R1 / дистилляты | 0.6 | 0.95 |
| V4 | 1.0 | 1.0 (агенты 0.95) |
