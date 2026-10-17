"""
Tool calling с локальным DeepSeek: полный цикл модель → функция → модель.

    pip install openai
    python tool_calling.py
Для llama-server запускайте его с флагом --jinja.
"""
import json

from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL = "deepseek-r1:14b"


def get_weather(city: str) -> dict:
    # заглушка — подключите реальный API погоды
    return {"city": city, "temp_c": 7, "conditions": "облачно"}


def calc(expression: str) -> dict:
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return {"error": "недопустимые символы"}
    return {"result": eval(expression, {"__builtins__": {}})}  # только арифметика


FUNCS = {"get_weather": get_weather, "calc": calc}
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Текущая погода в городе",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "Посчитать арифметическое выражение",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]


def run(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    for _ in range(5):  # защита от бесконечного цикла
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = FUNCS[call.function.name](**args)
            print(f"  → {call.function.name}({args}) = {result}")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)}
            )
    return "Превышен лимит шагов"


if __name__ == "__main__":
    print(run("Какая погода в Казани и сколько будет 17*23+4?"))
