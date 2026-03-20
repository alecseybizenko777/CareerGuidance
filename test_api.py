# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки API
"""
import sys
import requests
from config import BOT_TOKEN, API_BASE_URL

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_api():
    """Тестируем все методы API"""
    headers = {'Authorization': BOT_TOKEN}

    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ API MAX")
    print("=" * 60)

    # 1. Проверка бота
    print("\n1️⃣ Проверка информации о боте (GET /me)...")
    r = requests.get(f"{API_BASE_URL}/me", headers=headers)
    print(f"   Статус: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Бот: {r.json().get('name')}")
    else:
        print(f"   ❌ Ошибка: {r.text}")

    # 2. Проверка подписок (WebHook)
    print("\n2️⃣ Проверка подписок (GET /subscriptions)...")
    r = requests.get(f"{API_BASE_URL}/subscriptions", headers=headers)
    print(f"   Статус: {r.status_code}")
    if r.status_code == 200:
        subs = r.json()
        print(f"   Подписок: {subs}")
        if subs:
            print("   ⚠️  У бота есть WebHook подписка! Это блокирует Long Polling")
            print("   Нужно удалить WebHook командой DELETE /subscriptions")
    else:
        print(f"   Ответ: {r.text}")

    # 3. Проверка обновлений
    print("\n3️⃣ Получение обновлений (GET /updates)...")
    r = requests.get(f"{API_BASE_URL}/updates", headers=headers, params={'limit': 5, 'timeout': 5})
    print(f"   Статус: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        updates = data.get('updates', [])
        print(f"   ✅ Получено обновлений: {len(updates)}")
        print(f"   Marker: {data.get('marker')}")
        if updates:
            print(f"   Первое обновление: {updates[0].get('type')}")
    else:
        print(f"   ❌ Ошибка: {r.text}")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_api()
