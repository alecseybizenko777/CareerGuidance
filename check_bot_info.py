# -*- coding: utf-8 -*-
"""
Скрипт для проверки информации о боте по токену
Показывает: ID, username, имя и другие данные
"""
import sys
import requests
from config import BOT_TOKEN, API_BASE_URL

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_bot_info(token):
    """Получить информацию о боте"""
    url = f"{API_BASE_URL}/me"
    headers = {
        'Authorization': token
    }

    try:
        print("🔍 Запрос информации о боте...")
        print(f"📡 API URL: {url}")
        print(f"🔑 Токен: {token[:20]}...\n")

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            bot_data = response.json()

            print("=" * 60)
            print("✅ ИНФОРМАЦИЯ О БОТЕ ПОЛУЧЕНА")
            print("=" * 60)
            print()
            print(f"🤖 Имя бота:       {bot_data.get('name', 'Не указано')}")
            print(f"👤 Username:       @{bot_data.get('username', 'Не указан')}")
            print(f"🆔 User ID:        {bot_data.get('user_id', 'Не указан')}")
            print(f"🏷️  First Name:     {bot_data.get('first_name', 'Не указано')}")
            print(f"📝 Description:    {bot_data.get('description', 'Нет описания')[:50]}...")
            print(f"🤖 Is Bot:         {'Да' if bot_data.get('is_bot') else 'Нет'}")
            print()
            print("=" * 60)
            print()
            print("🔗 Ссылка на бота в MAX:")
            if bot_data.get('username'):
                print(f"   https://max.ru/{bot_data.get('username')}")
            else:
                print(f"   ID: {bot_data.get('user_id')} (username не установлен)")
            print()
            print("=" * 60)

            return bot_data

        elif response.status_code == 401:
            print("❌ ОШИБКА АУТЕНТИФИКАЦИИ")
            print("=" * 60)
            print("Токен недействителен или истек.")
            print("Проверьте токен в файле .env")
            return None

        else:
            print(f"❌ ОШИБКА: HTTP {response.status_code}")
            print("=" * 60)
            print(f"Ответ сервера: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ ОШИБКА: Превышено время ожидания")
        print("Проверьте интернет-соединение")
        return None

    except requests.exceptions.ConnectionError:
        print("❌ ОШИБКА: Не удается подключиться к API MAX")
        print("Проверьте интернет-соединение")
        return None

    except Exception as e:
        print(f"❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        return None

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("🤖 ПРОВЕРКА ИНФОРМАЦИИ О БОТЕ MAX")
    print("=" * 60)
    print()

    # Получить информацию
    bot_info = get_bot_info(BOT_TOKEN)

    if bot_info:
        print("\n✅ Бот настроен правильно! Можно запускать bot.py")
    else:
        print("\n❌ Не удалось получить информацию о боте")
        print("Проверьте токен в файле .env")

    print()
