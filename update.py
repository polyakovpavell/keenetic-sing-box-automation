#!/opt/bin/python3
# -*- coding: utf-8 -*-

import configparser
import urllib.request
import base64
import json
import subprocess
import os
import sys
from parsers import parse_nodes

# Определяем пути относительно расположения скрипта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.ini')
TEMPLATE_FILE = os.path.join(BASE_DIR, 'template.json')

def load_settings():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Файл настроек {CONFIG_FILE} не найден.")
        sys.exit(1)
    config.read(CONFIG_FILE, encoding='utf-8')
    return config

def fetch_subscription(url, user_agent, timeout):
    req = urllib.request.Request(url, headers={'User-Agent': user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            b64_data = response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"[ERROR] Ошибка скачивания подписки: {e}")
        sys.exit(1)

    # Выравнивание padding для Base64
    b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
    try:
        decoded = base64.b64decode(b64_data).decode('utf-8')
        return [line.strip() for line in decoded.splitlines() if line.strip()]
    except Exception as e:
        print(f"[ERROR] Ошибка декодирования Base64: {e}")
        sys.exit(1)

def main():
    settings = load_settings()
    sub_url = settings.get('subscription', 'url')
    timeout = settings.getint('subscription', 'timeout', fallback=25)
    user_agent = settings.get('subscription', 'user_agent')

    singbox_bin = settings.get('paths', 'singbox_bin')
    config_target = settings.get('paths', 'config_target')
    config_temp = settings.get('paths', 'config_temp')
    restart_cmd = settings.get('paths', 'restart_cmd').split()

    print("[INFO] Запуск обновления подписки...")
    uris = fetch_subscription(sub_url, user_agent, timeout)
    nodes = parse_nodes(uris)
    
    if not nodes:
        print("[ERROR] Не удалось распарсить ни одну ноду.")
        sys.exit(1)
        
    print(f"[INFO] Распарсено нод: {len(nodes)}")

    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Ошибка чтения шаблона {TEMPLATE_FILE}: {e}")
        sys.exit(1)

    node_tags = [n["tag"] for n in nodes]
    
    # Фильтрация узлов для YouTube: выбираем любые протоколы, содержащие ⚡
    youtube_tags = [n["tag"] for n in nodes if "⚡" in n["tag"]]
    if not youtube_tags:
        youtube_tags = node_tags[:50] # Резерв, если нет нод с молнией

    # Вставка узлов в шаблон конфигурации
    for outbound in config_data.get("outbounds", []):
        if outbound.get("tag") == "Proxy":
            # Сохраняем базовые ["YouTube-Fast", "DIRECT"] и добавляем узлы
            outbound["outbounds"].extend(node_tags)
        elif outbound.get("tag") == "YouTube-Fast":
            outbound["outbounds"] = youtube_tags[:50]

    config_data["outbounds"].extend(nodes)
    
    # Запись временного файла
    os.makedirs(os.path.dirname(config_temp), exist_ok=True)
    try:
        with open(config_temp, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Ошибка записи временного файла: {e}")
        sys.exit(1)

    print("[INFO] Валидация конфигурации через sing-box...")
    result = subprocess.run([singbox_bin, 'check', '-c', config_temp], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[INFO] Валидация успешна. Применение конфига и перезапуск...")
        try:
            os.replace(config_temp, config_target)
            subprocess.run(restart_cmd, check=True)
            print("[SUCCESS] Обновление успешно завершено!")
        except Exception as e:
            print(f"[ERROR] Ошибка применения конфигурации: {e}")
            sys.exit(1)
    else:
        print(f"[ERROR] Конфигурация отклонена бинарником sing-box! Код: {result.returncode}")
        print(f"[ERROR] Вывод sing-box:\n{result.stderr.strip()}")
        if os.path.exists(config_temp):
            os.remove(config_temp)
        sys.exit(1)

if __name__ == '__main__':
    main()
