# -*- coding: utf-8 -*-
"""
Очистка и пересоздание базы данных
"""
import sys
import os
from database import Database

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("⚠️  ВНИМАНИЕ: ОЧИСТКА БАЗЫ ДАННЫХ")
print("=" * 60)
print()
print("Это удалит ВСЕ данные:")
print("  - Все вопросы")
print("  - Все ПОО")
print("  - Всех пользователей")
print("  - Все результаты тестов")
print()

response = input("Вы уверены? Введите 'ДА' для подтверждения: ")

if response.strip().upper() != 'ДА':
    print("\n❌ Отменено")
    sys.exit(0)

print("\n🗑️  Удаление старой базы данных...")

if os.path.exists('bot_database.db'):
    os.remove('bot_database.db')
    print("✅ Старая база данных удалена")
else:
    print("ℹ️  Файл базы данных не найден")

print("\n📝 Создание новой базы данных...")
db = Database()
print("✅ Новая база данных создана")

print("\n" + "=" * 60)
print("✅ БАЗА ДАННЫХ УСПЕШНО ОЧИЩЕНА")
print("=" * 60)
print()
print("Теперь запустите: python load_data.py")
print()
