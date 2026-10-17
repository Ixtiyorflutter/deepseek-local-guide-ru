# Урок 13. Дообучение DeepSeek (fine-tuning) через QLoRA и Unsloth

[← Урок 12](12-troubleshooting.md) · [Оглавление](../README.md) · [Урок 14 →](14-ustanovka-po-os.md)

## Когда дообучение нужно, а когда нет

| Хочу, чтобы модель… | Решение |
|---|---|
| Знала факты из моих документов | **RAG** ([урок 10](10-rag-i-agenty.md)), а не дообучение |
| Отвечала в моём стиле и формате | ✅ Fine-tuning |
| Стабильно выдавала строгий JSON или шаблон | ✅ Fine-tuning (или JSON Schema) |
| Хорошо работала в узкой области (медицина, право, внутренний DSL) | ✅ Fine-tuning + RAG |
| Лучше говорила по-русски | ✅ Fine-tuning на качественных русских диалогах |

## Что понадобится

- NVIDIA GPU: 8–12 ГБ для 8B, 16 ГБ для 14B, 24+ ГБ для 32B (QLoRA, 4-бит). Или бесплатный Google Colab (T4, 16 ГБ).
- Python 3.10+.
- Датасет: 500–5000 качественных примеров. Качество важнее количества.

## Шаг 1. Датасет

Формат JSONL, одна строка — один диалог:

```json
{"messages": [{"role": "user", "content": "Что такое НДС?"}, {"role": "assistant", "content": "<think>Нужно дать краткое определение…</think>НДС — налог на добавленную стоимость…"}]}
```

Для reasoning-моделей полезно включать рассуждения в `<think>`, иначе модель может разучиться думать. Если рассуждения не нужны, используй примеры без них, а при инференсе отключай thinking.

## Шаг 2. Обучение LoRA в Unsloth

```bash
pip install unsloth
```

```python
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/DeepSeek-R1-Distill-Qwen-14B",
    max_seq_length=4096,
    load_in_4bit=True,          # QLoRA
)
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=16, lora_dropout=0,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)

ds = load_dataset("json", data_files="train.jsonl", split="train")
ds = ds.map(lambda x: {"text": tokenizer.apply_chat_template(x["messages"], tokenize=False)})

trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=ds,
    args=SFTConfig(
        dataset_text_field="text",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=2,
        learning_rate=2e-4,
        logging_steps=10,
        output_dir="out",
    ),
)
trainer.train()
```

> API Unsloth и TRL меняется, поэтому сверяйся с актуальными ноутбуками в [репозитории Unsloth](https://github.com/unslothai/unsloth).

## Шаг 3. Экспорт в GGUF

```python
model.save_pretrained_gguf("my-deepseek", tokenizer, quantization_method="q4_k_m")
```

## Шаг 4. Запуск в Ollama

```dockerfile
# Modelfile
FROM ./my-deepseek/unsloth.Q4_K_M.gguf
PARAMETER temperature 0.6
PARAMETER top_p 0.95
```

```bash
ollama create my-deepseek -f Modelfile
ollama run my-deepseek
```

## Советы

- **Начни с малого:** 1–2 эпохи. Переобучение заметно, когда модель повторяет датасет дословно.
- **Отложи 5–10% примеров** для проверки и сравнивай ответы до и после.
- **`r=16`** — хороший старт; `r=32–64` нужен для сложных задач и стоит больше памяти.
- **Не смешивай** в одном датасете разные шаблоны ответа.
- **Полный V4 дообучать дома нереально:** это задача для кластера. Дистилляты 8B–32B — оптимальный выбор.

[Урок 14: Установка по шагам →](14-ustanovka-po-os.md)
