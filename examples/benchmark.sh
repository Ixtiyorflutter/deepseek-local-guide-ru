#!/usr/bin/env bash
# Замер скорости генерации моделей DeepSeek в Ollama.
# Использование: ./benchmark.sh deepseek-r1:8b deepseek-r1:14b
set -euo pipefail

PROMPT="Напиши функцию на Python, которая проверяет, является ли число простым, и объясни её."
MODELS=("${@:-deepseek-r1:8b}")

printf "%-25s %15s %15s\n" "Модель" "prompt ток/с" "gen ток/с"
for m in "${MODELS[@]}"; do
  out=$(curl -s http://localhost:11434/api/generate \
    -d "{\"model\":\"$m\",\"prompt\":\"$PROMPT\",\"stream\":false,\"options\":{\"num_predict\":256}}")
  python3 - "$m" "$out" <<'PY'
import json, sys
m, raw = sys.argv[1], sys.argv[2]
d = json.loads(raw)
pp = d.get("prompt_eval_count", 0) / max(d.get("prompt_eval_duration", 1), 1) * 1e9
tg = d.get("eval_count", 0) / max(d.get("eval_duration", 1), 1) * 1e9
print(f"{m:<25} {pp:15.1f} {tg:15.1f}")
PY
done
