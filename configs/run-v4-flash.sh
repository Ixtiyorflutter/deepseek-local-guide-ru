#!/usr/bin/env bash
# Запуск DeepSeek-V4-Flash (GGUF) через llama-server.
# Режимы: ./run-v4-flash.sh unified   — Mac Studio / DGX Spark (всё в единой памяти)
#         ./run-v4-flash.sh hybrid    — одна GPU + много RAM (эксперты MoE на CPU)
set -euo pipefail

MODE="${1:-hybrid}"
LLAMA="${LLAMA:-./llama.cpp/build/bin/llama-server}"
MODEL="${MODEL:-models/V4-Flash/UD-IQ3_XXS/DeepSeek-V4-Flash-0731-UD-IQ3_XXS-00001-of-00004.gguf}"
CTX="${CTX:-32768}"
THREADS="${THREADS:-$(nproc 2>/dev/null || sysctl -n hw.physicalcpu)}"

COMMON=(-m "$MODEL" -c "$CTX" -t "$THREADS" -fa on
        --cache-type-k q8_0 --cache-type-v q8_0
        --temp 1.0 --top-p 1.0 --min-p 0.01
        --jinja --host 127.0.0.1 --port 8080)

case "$MODE" in
  unified) exec "$LLAMA" "${COMMON[@]}" -ngl 99 ;;
  hybrid)  exec "$LLAMA" "${COMMON[@]}" -ngl 99 -ot ".ffn_.*_exps.=CPU" ;;
  *) echo "Режим: unified | hybrid"; exit 1 ;;
esac
