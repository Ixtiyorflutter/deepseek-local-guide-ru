# Урок 14. Как установить DeepSeek: пошагово для Windows, macOS и Linux

[← Урок 13](13-fine-tuning.md) · [Оглавление](../README.md)

## 🪟 Windows 10 / 11

### 1. Проверь видеокарту

`Ctrl+Shift+Esc` → Диспетчер задач → Производительность → GPU. Запиши модель и «Выделенную память графического процессора».

### 2. Обнови драйвер

- **NVIDIA:** [nvidia.com/drivers](https://www.nvidia.com/Download/index.aspx) или NVIDIA App.
- **AMD:** AMD Software: Adrenalin Edition.

### 3. Установи Ollama

1. Скачай `OllamaSetup.exe` с [ollama.com/download](https://ollama.com/download).
2. Запусти установщик, Ollama появится в трее.
3. Открой **PowerShell** или **Терминал** и проверь:
   ```powershell
   ollama --version
   ```

### 4. Перенеси модели на другой диск (если диск C: маленький)

Пуск → «Изменение системных переменных среды» → Переменные среды → Создать:
`OLLAMA_MODELS` = `D:\ollama\models`. Перезапусти Ollama.

### 5. Запусти модель

```powershell
ollama run deepseek-r1:8b
```

### 6. Графический интерфейс

- Самый простой вариант — [LM Studio](https://lmstudio.ai) (без Docker).
- Или установи [Docker Desktop](https://www.docker.com/products/docker-desktop/) (включи WSL2) и запусти Open WebUI командой из README.

> 💡 Для llama.cpp на Windows скачай готовый архив `llama-…-bin-win-cuda-….zip` из [Releases](https://github.com/ggml-org/llama.cpp/releases). Кавычки в JSON-параметрах PowerShell пиши так: `"{\"enable_thinking\":false}"`.

## 🍎 macOS (Apple Silicon M1–M5)

### 1. Узнай объём памяти

 → Об этом Mac → Память. От этого зависит, какая модель поместится (см. README, часть 3).

### 2. Установи Ollama

```bash
brew install ollama        # или приложение с ollama.com/download
ollama serve &             # если ставил через brew
ollama run deepseek-r1:14b
```

### 3. Дай GPU больше памяти (для больших моделей)

```bash
sudo sysctl iogpu.wired_limit_mb=57344   # пример для Mac с 64 ГБ
```

### 4. LM Studio + MLX

В LM Studio на Mac выбирай модели с пометкой **MLX**: они часто быстрее GGUF.

### 5. llama.cpp

```bash
brew install llama.cpp
llama-server -hf unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF:Q4_K_M -ngl 99 -c 16384
```

## 🐧 Linux (Ubuntu / Debian)

### 1. Драйвер NVIDIA

```bash
sudo ubuntu-drivers autoinstall
sudo reboot
nvidia-smi        # должна показаться видеокарта
```

### 2. Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama
ollama run deepseek-r1:14b
```

### 3. Настройки через systemd

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_CONTEXT_LENGTH=32768"
Environment="OLLAMA_KEEP_ALIVE=-1"
```

```bash
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

### 4. Docker + GPU (для Open WebUI и vLLM)

```bash
curl -fsSL https://get.docker.com | sh
# NVIDIA Container Toolkit — по инструкции NVIDIA для своего дистрибутива
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

### 5. Весь стек одной командой

```bash
git clone https://github.com/justxor/deepseek-local-guide-ru
cd deepseek-local-guide-ru/configs
docker compose up -d
docker compose exec ollama ollama pull deepseek-r1:14b
# http://localhost:3000
```

## ✅ Проверка после установки

- [ ] `ollama run deepseek-r1:8b` отвечает
- [ ] `ollama ps` показывает `100% GPU`
- [ ] `ollama run deepseek-r1:8b --verbose` даёт адекватную скорость (`eval rate`)
- [ ] Интерфейс (LM Studio или Open WebUI) открывается и видит модель

[← К оглавлению](../README.md)
