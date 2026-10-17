# Урок 11. DeepSeek в продакшне: Docker, доступ, безопасность

[← Урок 10](10-rag-i-agenty.md) · [Оглавление](../README.md) · [Урок 12 →](12-troubleshooting.md)

## Архитектура для команды

```
Пользователи → HTTPS (nginx/Caddy) → Open WebUI (авторизация, роли)
                                        ↓
                         Ollama / llama-server / vLLM (только внутренняя сеть)
```

## Docker Compose

Готовый стек: [configs/docker-compose.yml](../configs/docker-compose.yml) — Ollama с GPU + Open WebUI.
Для vLLM: [configs/docker-compose.vllm.yml](../configs/docker-compose.vllm.yml).

## Безопасность — обязательный минимум

1. **Никогда не открывай порт 11434 (Ollama) в интернет.** API Ollama не имеет авторизации; в сети регулярно находят тысячи открытых серверов.
2. Бэкенд слушает `127.0.0.1` или внутреннюю docker-сеть. Наружу — только reverse-proxy с HTTPS.
3. Для llama-server / vLLM — `--api-key`.
4. В Open WebUI — отключи свободную регистрацию (`ENABLE_SIGNUP=false`) после создания админа.
5. Обновляй Ollama/llama.cpp — уязвимости в парсерах моделей находят регулярно.
6. Скачивай модели только из проверенных репозиториев (`deepseek-ai`, `unsloth`, `bartowski`, официальная библиотека Ollama). Предпочитай `safetensors`/GGUF, а не `pickle`-форматы.
7. Агентам с доступом к shell/файлам — песочница (Docker, отдельный пользователь) и подтверждение опасных действий.

## Reverse proxy (Caddy — HTTPS автоматически)

```caddyfile
ai.example.com {
    reverse_proxy localhost:3000
}
```

Готовый конфиг nginx: [configs/nginx.conf](../configs/nginx.conf).

## Мониторинг

- **vLLM / SGLang** отдают метрики Prometheus на `/metrics` — подключай Grafana.
- **GPU:** `nvidia-smi dmon`, `nvtop`, DCGM exporter.
- Логи Ollama: `journalctl -u ollama -f` (Linux).

## Приватность и цензура модели

- Локальная модель не отправляет данные — сеть используется только при загрузке.
- Модели DeepSeek обучены с ограничениями на ряд тем; локальный запуск этого не отменяет — ограничения в самих весах.
- Для чувствительных данных — изолированный контур без интернета: скачай модели заранее и перенеси файлы.

## Лицензирование

- Веса DeepSeek V3/R1/V4 — **MIT**: коммерческое использование разрешено.
- Дистилляты R1 — лицензия базовой модели (Qwen — Apache 2.0, Llama — Llama Community License).
- Всегда проверяй файл `LICENSE` в репозитории модели. Это не юридическая консультация.

[Урок 12: Траблшутинг →](12-troubleshooting.md)
