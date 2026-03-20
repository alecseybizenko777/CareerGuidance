# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота Max
BOT_TOKEN = os.getenv('VK_BOT_TOKEN', 'f9LHodD0cOJrQZ9iPZqMom9zEZQbFEYafmllyRhsWVQZtXGghVYiSTQrOiijttQyZnxcLFcVMUp55X4JFWFE')

# ID администратора (можно задать позже)
ADMIN_ID = os.getenv('ADMIN_ID', '')

# URL API Max
API_BASE_URL = 'https://platform-api.max.ru'

# Настройки Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
FLASK_HOST = '0.0.0.0'
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# База данных
DATABASE_PATH = 'bot_database.db'

# Критерии тестирования
CRITERIA = {
    'Human': 'Человек-человек',
    'Nature': 'Человек-природа',
    'Tech': 'Человек-техника',
    'Sign': 'Человек-знаковые системы',
    'Art': 'Человек-художественный образ'
}

# Минимальный балл для показа ПОО
MIN_SCORE_TO_SHOW = 10

# Режим отбора ПОО: 'threshold' (по порогу) или 'top1' (только топ-1 критерий)
POO_SELECTION_MODE = 'threshold'

# Разрешить пропуск вопросов
ALLOW_SKIP_QUESTIONS = True
