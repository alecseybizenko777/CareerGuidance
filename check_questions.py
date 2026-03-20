# -*- coding: utf-8 -*-
"""
Проверка вопросов в базе данных
"""
import sys
from database import Database

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

db = Database()

print("=" * 60)
print("🔍 ПРОВЕРКА ВОПРОСОВ В БАЗЕ ДАННЫХ")
print("=" * 60)

questions = db.get_all_questions()
total = db.get_total_questions_count()

print(f"\n📊 Всего вопросов в БД: {total}")
print(f"📊 Получено из БД: {len(questions)}")
print()

if questions:
    print("Первые 5 вопросов:")
    for q in questions[:5]:
        print(f"  {q['question_order']}. {q['option1_text'][:50]}...")

    print()
    print("Последние 5 вопросов:")
    for q in questions[-5:]:
        print(f"  {q['question_order']}. {q['option1_text'][:50]}...")
else:
    print("⚠️  Вопросов нет в базе данных!")

print()
print("=" * 60)

# Проверяем есть ли 31-й вопрос
q31 = db.get_question_by_order(31)
if q31:
    print("✅ Вопрос 31 найден")
else:
    print("❌ Вопрос 31 НЕ найден (это нормально, если у нас 30 вопросов)")

print("=" * 60)
