# -*- coding: utf-8 -*-
"""
Отладочный скрипт для просмотра обновлений
"""
import sys
import requests
import json
from config import BOT_TOKEN, API_BASE_URL

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'Authorization': BOT_TOKEN}

print("=" * 60)
print("🔍 ПРОСМОТР ОБНОВЛЕНИЙ (БЕЗ MARKER)")
print("=" * 60)
print()

# Получаем обновления без marker - получим все что есть
response = requests.get(
    f"{API_BASE_URL}/updates",
    headers=headers,
    params={'limit': 100, 'timeout': 5}
)

if response.status_code == 200:
    data = response.json()
    updates = data.get('updates', [])
    marker = data.get('marker')

    print(f"📊 Статус: {response.status_code}")
    print(f"📦 Получено обновлений: {len(updates)}")
    print(f"🔖 Marker: {marker}")
    print()

    if updates:
        print("=" * 60)
        print("СПИСОК ОБНОВЛЕНИЙ:")
        print("=" * 60)
        for i, update in enumerate(updates, 1):
            print(f"\n{i}. Тип: {update.get('type')}")
            print(f"   Update ID: {update.get('update_id')}")
            print(f"   Timestamp: {update.get('timestamp')}")

            # Показываем payload
            payload = update.get('payload', {})

            if update.get('type') == 'message_created':
                sender = payload.get('sender', {})
                body = payload.get('body', {})
                print(f"   От: {sender.get('first_name')} (ID: {sender.get('user_id')})")
                print(f"   Текст: {body.get('text')}")

            elif update.get('type') == 'bot_started':
                user = payload.get('user', {})
                print(f"   Пользователь: {user.get('first_name')} (ID: {user.get('user_id')})")
                print(f"   Chat ID: {payload.get('chat_id')}")

            elif update.get('type') == 'message_callback':
                callback = payload.get('callback', {})
                user = callback.get('user', {})
                print(f"   Пользователь: {user.get('first_name')} (ID: {user.get('user_id')})")
                print(f"   Payload: {callback.get('payload')}")

        print()
        print("=" * 60)
    else:
        print("ℹ️  Нет новых обновлений")
        print()
        print("💡 Попробуйте:")
        print("   1. Отправить боту новое сообщение")
        print("   2. Перезапустить бота (он сохранит marker)")
        print("   3. Проверить, что бот не запущен в другом месте")

else:
    print(f"❌ Ошибка: {response.status_code}")
    print(f"Ответ: {response.text}")

print()
print("=" * 60)
print()
print("🔧 ПОЛНЫЙ JSON ОТВЕТ:")
print("=" * 60)
print(json.dumps(data if response.status_code == 200 else {}, indent=2, ensure_ascii=False))
