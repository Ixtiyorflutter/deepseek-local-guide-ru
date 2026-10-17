"""
Простой консольный чат с локальным DeepSeek через OpenAI-совместимый API.
Работает с Ollama, llama-server, LM Studio, vLLM.

    pip install openai
    python chat_cli.py --model deepseek-r1:8b
    python chat_cli.py --base-url http://localhost:8080/v1 --model any
"""
import argparse
import re

from openai import OpenAI

THINK_RE = re.compile(r"<think>.*?</think>", re.S)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:11434/v1")
    p.add_argument("--model", default="deepseek-r1:8b")
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--system", default="Отвечай на русском языке.")
    args = p.parse_args()

    client = OpenAI(base_url=args.base_url, api_key="local")
    history = [{"role": "system", "content": args.system}]

    print(f"Модель: {args.model}. Пустая строка или 'exit' — выход.\n")
    while True:
        user = input("Вы: ").strip()
        if not user or user.lower() in {"exit", "quit", "выход"}:
            break
        history.append({"role": "user", "content": user})

        print("DeepSeek: ", end="", flush=True)
        full = ""
        stream = client.chat.completions.create(
            model=args.model,
            messages=history,
            temperature=args.temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            # некоторые бэкенды отдают рассуждения отдельным полем
            reasoning = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
            if reasoning:
                print(f"\033[2m{reasoning}\033[0m", end="", flush=True)
            if delta.content:
                print(delta.content, end="", flush=True)
                full += delta.content
        print("\n")

        # в историю — только ответ, без рассуждений (экономия контекста)
        history.append({"role": "assistant", "content": THINK_RE.sub("", full).strip()})


if __name__ == "__main__":
    main()
