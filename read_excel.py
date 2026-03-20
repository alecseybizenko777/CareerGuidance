# -*- coding: utf-8 -*-
import openpyxl
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('zip/СПО критерии по Климову.xlsx')
sheet = wb.active

print("Структура таблицы:")
print("-" * 100)
for i, row in enumerate(sheet.iter_rows(values_only=True), 1):
    print(f"Строка {i}: {row}")
    if i > 15:
        break
