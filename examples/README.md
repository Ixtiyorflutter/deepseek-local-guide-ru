# Примеры кода для локального DeepSeek

| Файл | Что делает |
|---|---|
| [chat_cli.py](chat_cli.py) | Консольный чат со стримингом и показом рассуждений |
| [rag_minimal.py](rag_minimal.py) | RAG по папке документов на `bge-m3` + DeepSeek |
| [tool_calling.py](tool_calling.py) | Вызов функций (погода, калькулятор), полный цикл |
| [benchmark.sh](benchmark.sh) | Замер скорости нескольких моделей в Ollama |

```bash
pip install -r requirements.txt
```

Все примеры по умолчанию работают с Ollama (`http://localhost:11434/v1`). Для другого бэкенда поменяйте `base_url` — см. [урок 7](../docs/07-api-i-integracii.md).
