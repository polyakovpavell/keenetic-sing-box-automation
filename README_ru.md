# 🚀 Sing-Box Subscription Updater & Smart Router

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Stdlib)-brightgreen.svg)]()
[![Sing-Box](https://img.shields.io/badge/Core-sing--box-orange.svg)](https://sing-box.sagernet.org/)
[![Platform](https://img.shields.io/badge/Platform-Entware%20%7C%20OpenWrt%20%7C%20Linux-lightgrey.svg)]()

🌐 **Язык / Language:** [🇷🇺 Русский](README_ru.md) | [🇬🇧 English](README_ru.md)

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