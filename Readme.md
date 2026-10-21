# 🚀 Sing-Box Subscription Updater & Smart Router

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Stdlib)-brightgreen.svg)]()
[![Sing-Box](https://img.shields.io/badge/Core-sing--box-orange.svg)](https://sing-box.sagernet.org/)
[![Platform](https://img.shields.io/badge/Platform-Entware%20%7C%20OpenWrt%20%7C%20Linux-lightgrey.svg)]()

🌐 **Язык / Language:** [🇷🇺 Русский](#-описание-проекта-ru) | [🇬🇧 English](#-project-overview-en)

---

## 🇷🇺 Описание проекта (RU)

Отказоустойчивая система автоматического обновления подписок, парсинга узлов и генерации правил умной маршрутизации (Split Tunneling) для ядра **sing-box**, работающего в среде **Entware** (роутеры Keenetic, Asuswrt-Merlin, OpenWrt и др.).

Проект спроектирован по принципам **Zero-Dependency** (используется исключительно стандартная библиотека Python) и **Safe Deployment** (валидация конфигурации перед атомарным применением), что делает его идеальным для встраиваемых систем с ограниченными ресурсами.

### ✨ Ключевые возможности (Architecture Highlights)

* **Zero-Dependency:** Не требует установки сторонних пакетов через `pip` (`requests`, `pydantic` и т.д.). Работает «из коробки» на любом минимальном образе Python 3 в Entware.
* **Мультипротокольный парсер:**
  * Полная поддержка **VLESS** (`TLS`, `Reality`, `XTLS-RPRX-Vision`, кастомные `uTLS` отпечатки, транспорт `gRPC`).
  * Полная поддержка **Hysteria2** (`hy2`, `ALPN`, управление `insecure`).
  * Автоматическая дедупликация тегов узлов (`Node_1`, `Node_2`).
* **Умная балансировка по тегам (`urltest`):**
  * Скрипт автоматически фильтрует узлы из подписки по маркерам в названиях и формирует специализированные группы отказоустойчивости (до 50 нод в пуле):
    * `YouTube-Fast`: высокоскоростные ноды с маркером `⚡` (с автоматическим исключением узлов РФ `🇷🇺`).
    * `Gemini-Fast`: ноды с чистыми / Residential IP с маркером `⭐️` (также за пределами РФ) для бесперебойной работы AI-сервисов.
* **Атомарный деплой и защита от сбоев (Safe Rollout):**
  * Сборка новой конфигурации происходит во временном файле (`/opt/tmp/config_temp.json`).
  * Перед применением конфигурация проходит строгую проверку бинарником `sing-box check`.
  * Только при успешной валидации (`exit code 0`) происходит атомарная подмена боевого конфига (`os.replace`) и перезапуск демона. Если подписка вернула битые данные — туннель продолжит работать на старом конфиге.
* **Встроенный L7 Watchdog (`--check`):**
  * Поддержка режима быстрой проверки жизнеспособности туннеля (проверка ответа от `https://www.youtube.com/generate_204`). Если туннель работает штатно — скрипт завершает работу без перезапуска сервиса; при деградации — запускает процедуру аварийного обновления и рестарта.
* **Продвинутая маршрутизация (Template Engine):**
  * **FakeIP + Persistent Cache:** Использование виртуального пула `198.18.0.0/15` с сохранением состояния в `/opt/etc/sing-box/cache.db` и блокировкой `HTTPS/SVCB` DNS-запросов.
  * **Блокировка QUIC (UDP/443):** Принудительный перевод трафика YouTube, Meta, Notion, Anthropic и Gemini на TCP для стабильной работы через прокси.
  * **Удаленные бинарные гео-базы (`.srs`):** Автоматическая подгрузка актуальных списков `SagerNet` и `runetfreedom` (включая точечную маршрутизацию аналитических доменов `statsig`, `sift` и IP-подсетей Telegram).

---

### 📂 Структура проекта

```text
.
├── .env              # Секретный файл со ссылкой на подписку (не коммитится в Git)
├── config.ini        # Системные пути, таймауты и настройки User-Agent
├── template.json     # Базовый шаблон sing-box (DNS, Inbounds, Route, каркас Outbounds)
├── parsers.py        # Модуль парсинга URI-ссылок (vless://, hysteria2://, hy2://)
├── update.py         # Главный оркестратор: скачивание, фильтрация, валидация и рестарт
└── config.json       # Итоговый (сгенерированный) конфигурационный файл sing-box
```

---

### ⚙️ Требования

* Роутер или сервер с установленной средой **Entware** / Linux.
* Установленный пакет **sing-box** (`/opt/bin/sing-box`).
* Установленный интерпретатор **Python 3** (`/opt/bin/python3`).

---

### 🚀 Установка и настройка

#### 1. Клонирование файлов
Разместите скрипты проекта в рабочей директории (например, `/opt/etc/sing-box/scripts/`):

```bash
mkdir -p /opt/etc/sing-box/scripts
cd /opt/etc/sing-box/scripts
# Скопируйте сюда update.py, parsers.py, template.json и config.ini
chmod +x update.py
```

#### 2. Настройка переменных окружения (`.env`)
Создайте файл `.env` рядом со скриптом `update.py` и укажите вашу ссылку на Base64-подписку:

```ini
URL="https://your-subscription-provider.com/api/v1/client/subscribe?token=YOUR_SECRET_TOKEN"
```

#### 3. Проверка путей в `config.ini`
При необходимости скорректируйте пути до бинарного файла и init-скрипта в `config.ini`:

```ini
[subscription]
timeout = 25
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

[paths]
singbox_bin = /opt/bin/sing-box
config_target = /opt/etc/sing-box/config.json
config_temp = /opt/tmp/config_temp.json
restart_cmd = /opt/etc/init.d/S99sing-box restart
```

---

### 🛠 Использование и Автоматизация (Cron)

#### Ручной запуск (принудительное обновление)
```bash
/opt/bin/python3 /opt/etc/sing-box/scripts/update.py
```

#### Запуск в режиме проверки (Watchdog / Failover)
```bash
/opt/bin/python3 /opt/etc/sing-box/scripts/update.py --check
```

#### Настройка планировщика `cron`
Для полной автоматизации добавьте две задачи в `/opt/etc/crontab`:
1. Плановое обновление подписки каждые 6 часов.
2. Проверка доступности туннеля каждые 5 минут с автоматическим восстановлением при падении.

```cron
# Плановое обновление узлов подписки (каждые 6 часов)
0 */6 * * * root /opt/bin/python3 /opt/etc/sing-box/scripts/update.py >/dev/null 2>&1

# Watchdog: проверка туннеля каждые 5 минут и аварийное восстановление
*/5 * * * * root /opt/bin/python3 /opt/etc/sing-box/scripts/update.py --check >/dev/null 2>&1
```

---

### 🔒 Безопасность (DevOps Best Practices)

Перед публикацией проекта в публичный Git-репозиторий **обязательно** добавьте в `.gitignore` файлы, содержащие чувствительные данные (ключи, UUID, пароли и адреса серверов):

```gitignore
.env
config.json
config_temp.json
*.db
__pycache__/
```

---
---

## 🇬🇧 Project Overview (EN)

A fault-tolerant subscription updater, node parser, and smart-routing (Split Tunneling) configuration generator for **sing-box**, specifically tailored for **Entware** environments (Keenetic, Asuswrt-Merlin, OpenWrt, and embedded Linux routers).

Engineered with **Zero-Dependency** (relying strictly on the Python 3 Standard Library) and **Atomic Safe Deployment** principles, making it lightweight, resilient, and production-ready for resource-constrained hardware.

### ✨ Key Features & Architecture

* **Zero-Dependency:** Runs purely on Python's standard library (`urllib`, `base64`, `json`, `configparser`, `subprocess`). No `pip` or external packages required.
* **Multi-Protocol URI Parser:**
  * Full **VLESS** support (`TLS`, `Reality`, `XTLS-RPRX-Vision` flow, custom `uTLS` fingerprints, `gRPC` transport).
  * Full **Hysteria2** support (`hy2`, `ALPN` negotiation, `insecure` flag handling).
  * Automatic node tag deduplication (`Node_1`, `Node_2`).
* **Smart Tag-Based Load Balancing (`urltest`):**
  * Automatically categorizes parsed nodes using emoji markers in node names and populates dedicated `urltest` outbound pools (capped at 50 nodes per pool):
    * `YouTube-Fast`: High-bandwidth nodes marked with `⚡` (automatically excluding Russian `🇷🇺` exit nodes).
    * `Gemini-Fast`: Clean / Residential IP nodes marked with `⭐️` (excluding `🇷🇺` nodes) for reliable access to AI platforms.
* **Atomic Deployment & Validation (Safe Rollout):**
  * Builds the candidate configuration in a temporary path (`/opt/tmp/config_temp.json`).
  * Validates syntax and schema using the native `sing-box check` command before touching production files.
  * Performs an atomic file replacement (`os.replace`) and restarts the daemon **only** if validation succeeds (`exit code 0`), preventing network blackouts caused by corrupted upstream subscriptions.
* **Self-Healing L7 Watchdog (`--check`):**
  * Includes a lightweight healthcheck flag that probes `https://www.youtube.com/generate_204`. If the tunnel responds within 5 seconds, the script exits cleanly (`0`). If the probe fails, it automatically triggers an emergency subscription pull and service restart.
* **Advanced Routing & Anti-DPI (`template.json`):**
  * **FakeIP + Persistent Cache:** Utilizes the `198.18.0.0/15` FakeIP range backed by `/opt/etc/sing-box/cache.db` and rejects `HTTPS/SVCB` DNS queries.
  * **QUIC (UDP/443) Blocking:** Forces TCP fallback for YouTube, Meta, Notion, Anthropic, and Google Gemini to prevent UDP throttling and improve proxy stability.
  * **Remote Binary Rule-Sets (`.srs`):** Dynamically fetches rule-sets from `SagerNet` and `runetfreedom`, alongside explicit routing for telemetry/auth domains (`statsig`, `sift`) and Telegram IP CIDRs.

---

### 📂 Project Structure

```text
.
├── .env              # Environment file storing the secret subscription URL (Git-ignored)
├── config.ini        # System paths, HTTP timeouts, and User-Agent configuration
├── template.json     # Base sing-box template (DNS, Inbounds, Route, Outbound skeletons)
├── parsers.py        # URI parsing engine for vless://, hysteria2://, and hy2://
├── update.py         # Main orchestrator: fetch, filter, validate, deploy, and watchdog
└── config.json       # Generated production sing-box configuration file
```

---

### ⚙️ Prerequisites

* Router or Linux host running **Entware** / OpenWrt.
* **sing-box** binary installed (`/opt/bin/sing-box`).
* **Python 3** installed (`/opt/bin/python3`).

---

### 🚀 Installation & Setup

#### 1. Deploy Scripts
Place the project files in your target directory (e.g., `/opt/etc/sing-box/scripts/`):

```bash
mkdir -p /opt/etc/sing-box/scripts
cd /opt/etc/sing-box/scripts
# Copy update.py, parsers.py, template.json, and config.ini here
chmod +x update.py
```

#### 2. Configure `.env`
Create a `.env` file in the same directory as `update.py` containing your Base64 subscription URL:

```ini
URL="https://your-subscription-provider.com/api/v1/client/subscribe?token=YOUR_SECRET_TOKEN"
```

#### 3. Verify `config.ini`
Adjust system paths and service restart commands in `config.ini` if your environment differs from standard Entware:

```ini
[subscription]
timeout = 25
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

[paths]
singbox_bin = /opt/bin/sing-box
config_target = /opt/etc/sing-box/config.json
config_temp = /opt/tmp/config_temp.json
restart_cmd = /opt/etc/init.d/S99sing-box restart
```

---

### 🛠 Usage & Cron Automation

#### Manual Update
```bash
/opt/bin/python3 /opt/etc/sing-box/scripts/update.py
```

#### Healthcheck / Watchdog Mode
```bash
/opt/bin/python3 /opt/etc/sing-box/scripts/update.py --check
```

#### Cron Setup (`/opt/etc/crontab`)
Set up automated subscription updates and self-healing checks:

```cron
# Scheduled subscription update (every 6 hours)
0 */6 * * * root /opt/bin/python3 /opt/etc/sing-box/scripts/update.py >/dev/null 2>&1

# Self-healing Watchdog: check tunnel every 5 minutes and recover on failure
*/5 * * * * root /opt/bin/python3 /opt/etc/sing-box/scripts/update.py --check >/dev/null 2>&1
```

---

### 🔒 Security Notice

Before pushing this repository to GitHub/GitLab, ensure that `.env` and `config.json` (which contains your parsed private `uuid`, `password`, and server IPs) are excluded via `.gitignore`:

```gitignore
.env
config.json
config_temp.json
*.db
__pycache__/
```