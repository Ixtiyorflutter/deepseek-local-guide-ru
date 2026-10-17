# Урок 6. Интерфейсы для DeepSeek: Open WebUI, LM Studio, Jan

[← Урок 5](05-vllm-sglang.md) · [Оглавление](../README.md) · [Урок 7 →](07-api-i-integracii.md)

## Open WebUI — «свой ChatGPT»

Самый популярный веб-интерфейс для локальных моделей: чаты, история, загрузка документов (RAG), веб-поиск, голос, несколько пользователей с ролями.

### Если Ollama уже установлен

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Всё в одном (Ollama + Open WebUI)

```bash
cd configs
docker compose up -d
```

См. [configs/docker-compose.yml](../configs/docker-compose.yml).

### Подключить llama.cpp / vLLM вместо Ollama

**Настройки администратора → Подключения → OpenAI API** → добавить:

- URL: `http://host.docker.internal:8080/v1` (llama-server) или `:8000/v1` (vLLM)
- Ключ: любой (или тот, что задан через `--api-key`)

### Фишки Open WebUI

- **Рассуждения сворачиваются** в блок «Думал N секунд» — удобно читать.
- **`#` в поле ввода** — прикрепить документ или сайт к сообщению.
- **Workspace → Models** — создай «персону» поверх DeepSeek со своим системным промптом и параметрами.
- **Knowledge** — загрузи базу документов один раз, используй во всех чатах.
- **Arena** — сравнение двух моделей вслепую.

## LM Studio — лучший вариант для новичков

1. Скачай с [lmstudio.ai](https://lmstudio.ai).
2. Вкладка поиска → `deepseek` → выбери модель и квант (зелёная метка — влезает в твою GPU).
3. Чат или вкладка **Developer → Start Server** — OpenAI-совместимый API на `http://localhost:1234/v1`.

**Фишки:** на Mac использует MLX (часто быстрее GGUF), наглядный выбор слоёв на GPU, CLI `lms` для автоматизации.

## Jan

[jan.ai](https://jan.ai) — открытое десктоп-приложение, полностью офлайн, со встроенным локальным API-сервером. Хорошая открытая альтернатива LM Studio.

## Другие варианты

| Инструмент | Особенность |
|---|---|
| **AnythingLLM** | Ориентирован на работу с документами и рабочие пространства |
| **LibreChat** | Клон интерфейса ChatGPT, много провайдеров |
| **Msty** | Десктоп, параллельные чаты с разными моделями |
| **Page Assist** | Расширение браузера: чат с текущей страницей через Ollama |
| **Встроенный UI llama-server** | Ничего ставить не нужно — `http://localhost:8080` |

[Урок 7: API и интеграции →](07-api-i-integracii.md)
