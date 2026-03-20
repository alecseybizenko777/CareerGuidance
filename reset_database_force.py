# -*- coding: utf-8 -*-
"""
Принудительная очистка и пересоздание базы данных
"""
import sys
import os
from database import Database

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("🗑️  ОЧИСТКА БАЗЫ ДАННЫХ")
print("=" * 60)

if os.path.exists('bot_database.db'):
    os.remove('bot_database.db')
    print("✅ Старая база данных удалена")
else:
    print("ℹ️  Файл базы данных не найден")

print("\n📝 Создание новой базы данных...")
db = Database()
print("✅ Новая база данных создана")

print("\n" + "=" * 60)
print("✅ ГОТОВО! Теперь запустите:")
print("   python load_data.py")
print("=" * 60)
