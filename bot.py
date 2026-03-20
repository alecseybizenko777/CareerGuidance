# -*- coding: utf-8 -*-
"""
Бот для Max (VK) - Профориентационное тестирование
"""
import sys
import time
import requests
import json
import random
from database import Database
from config import BOT_TOKEN, API_BASE_URL, CRITERIA, MIN_SCORE_TO_SHOW, POO_SELECTION_MODE, ALLOW_SKIP_QUESTIONS

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class MaxBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.api_url = API_BASE_URL
        self.db = Database()
        self.marker = None
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }

    def reload_config(self):
        """Перезагрузить настройки из config.py"""
        import importlib
        import config as cfg
        importlib.reload(cfg)

        # Обновить глобальные переменные
        global MIN_SCORE_TO_SHOW, POO_SELECTION_MODE, ALLOW_SKIP_QUESTIONS
        MIN_SCORE_TO_SHOW = cfg.MIN_SCORE_TO_SHOW
        POO_SELECTION_MODE = cfg.POO_SELECTION_MODE
        ALLOW_SKIP_QUESTIONS = cfg.ALLOW_SKIP_QUESTIONS

    def api_request(self, method, endpoint, data=None, params=None):
        """Общий метод для выполнения API запросов"""
        url = f"{self.api_url}{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params, timeout=90)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            else:
                return None

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Исключение при запросе: {e}")
            return None

    def get_updates(self):
        """Получить обновления через Long Polling"""
        params = {
            'limit': 10,
            'timeout': 30
        }

        if self.marker:
            params['marker'] = self.marker

        result = self.api_request('GET', '/updates', params=params)

        if result:
            self.marker = result.get('marker')
            return result.get('updates', [])

        return []

    def send_message(self, chat_id, text, keyboard=None):
        """Отправить сообщение"""
        data = {
            'text': text,
            'format': 'markdown'
        }

        if keyboard:
            data['attachments'] = [
                {
                    'type': 'inline_keyboard',
                    'payload': {
                        'buttons': keyboard
                    }
                }
            ]

        params = {'chat_id': chat_id}
        return self.api_request('POST', '/messages', data=data, params=params)

    def send_welcome_message(self, chat_id):
        """Приветственное сообщение"""
        text = """👋 **Добро пожаловать в бот профориентационного тестирования!**

Этот тест поможет вам определить наиболее подходящую профессиональную сферу по методике Климова.

📋 **Тест включает 30 вопросов**

Каждый вопрос содержит два варианта деятельности. Выберите тот, который вам больше нравится.

После завершения теста вы получите рекомендации по выбору учебного заведения.

Нажмите кнопку ниже, чтобы начать тестирование!"""

        keyboard = [
            [
                {
                    'type': 'callback',
                    'text': '🚀 Начать тестирование',
                    'payload': json.dumps({'action': 'start_test'})
                }
            ]
        ]

        self.send_message(chat_id, text, keyboard)

    def start_test(self, user_id, chat_id):
        """Начать новый тест"""
        # Создать запись в БД
        test_id = self.db.start_test(user_id)

        # Отправить первый вопрос
        self.send_question(chat_id, user_id, 1)

        return test_id

    def send_question(self, chat_id, user_id, question_num):
        """Отправить вопрос"""
        # Перезагрузить настройки перед отправкой вопроса
        self.reload_config()

        # Получить вопрос из БД
        question = self.db.get_question_by_order(question_num)

        if not question:
            self.send_message(chat_id, "❌ Ошибка: вопрос не найден")
            return

        total = self.db.get_total_questions_count()

        # ИСПРАВЛЕНО: Вопросы в тексте сообщения, кнопки короткие
        text = f"""**Вопрос {question_num} из {total}**

Что вам больше нравится?

**А)** {question['option1_text']}

**Б)** {question['option2_text']}"""

        keyboard = [
            [
                {
                    'type': 'callback',
                    'text': '✅ Вариант А',
                    'payload': json.dumps({
                        'action': 'answer',
                        'question': question_num,
                        'option': 1,
                        'criteria': question['option1_criteria']
                    })
                },
                {
                    'type': 'callback',
                    'text': '✅ Вариант Б',
                    'payload': json.dumps({
                        'action': 'answer',
                        'question': question_num,
                        'option': 2,
                        'criteria': question['option2_criteria']
                    })
                }
            ]
        ]

        # Добавить кнопку "Пропустить" если включена в настройках
        if ALLOW_SKIP_QUESTIONS:
            keyboard.append([
                {
                    'type': 'callback',
                    'text': '⏭️ Пропустить вопрос',
                    'payload': json.dumps({
                        'action': 'skip',
                        'question': question_num
                    })
                }
            ])

        self.send_message(chat_id, text, keyboard)

    def process_answer(self, user_id, chat_id, question_num, option, criteria):
        """Обработать ответ на вопрос"""
        # Получить активный тест
        test = self.db.get_active_test(user_id)

        if not test:
            self.send_message(chat_id, "❌ Активный тест не найден. Начните новый тест.")
            return

        # Сохранить ответ
        self.db.update_test_answer(test['id'], question_num, option, criteria)

        # Проверить, последний ли это вопрос
        total = self.db.get_total_questions_count()

        if question_num >= total:
            # Завершить тест
            self.complete_test(user_id, chat_id, test['id'])
        else:
            # Отправить следующий вопрос
            self.send_question(chat_id, user_id, question_num + 1)

    def skip_question(self, user_id, chat_id, question_num):
        """Пропустить вопрос без начисления баллов"""
        # Получить активный тест
        test = self.db.get_active_test(user_id)

        if not test:
            self.send_message(chat_id, "❌ Активный тест не найден. Начните новый тест.")
            return

        # Проверить, последний ли это вопрос
        total = self.db.get_total_questions_count()

        if question_num >= total:
            # Завершить тест
            self.complete_test(user_id, chat_id, test['id'])
        else:
            # Отправить следующий вопрос (без сохранения ответа)
            self.send_question(chat_id, user_id, question_num + 1)

    def complete_test(self, user_id, chat_id, test_id):
        """Завершить тест и показать результаты"""
        # Перезагрузить настройки перед завершением теста
        self.reload_config()

        # Пометить тест как завершенный
        self.db.complete_test(test_id)

        # Получить результаты
        results = self.db.get_test_results(test_id)

        if not results:
            self.send_message(chat_id, "❌ Ошибка получения результатов")
            return

        # Составить результаты
        scores = {
            'Human': results['score_human'],
            'Nature': results['score_nature'],
            'Tech': results['score_tech'],
            'Sign': results['score_sign'],
            'Art': results['score_art']
        }

        # Текст результатов
        result_text = "🎉 **Тест завершен!**\n\n📊 **Ваши результаты:**\n\n"

        for criteria_code, criteria_name in CRITERIA.items():
            score = scores[criteria_code]
            result_text += f"• {criteria_name}: **{score} баллов**\n"

        # Определить критерии для подбора ПОО в зависимости от режима
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if POO_SELECTION_MODE == 'top1':
            # РЕЖИМ 1: Только ТОП-1 критерий
            top_criteria_code = sorted_scores[0][0]
            top_criteria_score = sorted_scores[0][1]

            # Проверить, что топ-1 набрал >= MIN_SCORE_TO_SHOW баллов
            if top_criteria_score < MIN_SCORE_TO_SHOW:
                result_text += f"\n❗ К сожалению, ни один из критериев не набрал минимум {MIN_SCORE_TO_SHOW} баллов. Попробуйте пройти тест еще раз."
                self.send_message(chat_id, result_text)
                return

            # Найти подходящие ПОО только по ТОП-1 критерию
            selected_criteria = [top_criteria_code]

            # Показать по какому критерию подбираются ПОО
            top_criteria_name = CRITERIA[top_criteria_code]
            result_text += f"\n\n🎯 **Ваше главное направление:**\n"
            result_text += f"• {top_criteria_name} ({top_criteria_score} баллов)\n"

        else:  # POO_SELECTION_MODE == 'threshold'
            # РЕЖИМ 2: Все критерии с баллами >= MIN_SCORE_TO_SHOW
            high_criteria = [(code, score) for code, score in sorted_scores if score >= MIN_SCORE_TO_SHOW]

            if not high_criteria:
                result_text += f"\n❗ К сожалению, ни один из критериев не набрал минимум {MIN_SCORE_TO_SHOW} баллов. Попробуйте пройти тест еще раз."
                self.send_message(chat_id, result_text)
                return

            selected_criteria = [code for code, score in high_criteria]

            # Показать все подходящие направления
            result_text += f"\n\n🎯 **Ваши сильные направления:**\n"
            for code, score in high_criteria:
                result_text += f"• {CRITERIA[code]}: **{score} баллов**\n"

        # Найти подходящие ПОО
        all_organizations = self.db.get_organizations_by_criteria(selected_criteria)

        # Ограничить вывод до 5-10 случайных ПОО
        if len(all_organizations) > 10:
            organizations = random.sample(all_organizations, random.randint(5, 10))
        else:
            organizations = all_organizations

        result_text += f"\n✅ **Рекомендуемые учебные заведения ({len(organizations)}):**\n\n"

        if organizations:
            for i, org in enumerate(organizations, 1):
                result_text += f"{i}. [{org['name']}]({org['url']})\n"
        else:
            result_text += "К сожалению, подходящих учебных заведений не найдено."

        result_text += "\n\n💡 Хотите пройти тест еще раз? Нажмите /start"

        self.send_message(chat_id, result_text)

    def handle_message_created(self, update):
        """Обработать новое сообщение"""
        # В MAX API структура: update.message содержит всё
        message = update.get('message', {})

        # Получить sender и recipient
        sender = message.get('sender', {})
        recipient = message.get('recipient', {})
        body = message.get('body', {})

        user_id = sender.get('user_id')
        chat_id = recipient.get('chat_id')
        text = body.get('text', '').strip()

        if not user_id or not chat_id:
            print(f"⚠️  Не удалось получить user_id или chat_id")
            return

        # Сохранить пользователя
        self.db.add_or_update_user(
            user_id=user_id,
            chat_id=chat_id,
            username=sender.get('username'),
            first_name=sender.get('first_name'),
            last_name=sender.get('last_name')
        )

        print(f"📨 Сообщение от {sender.get('first_name')} (ID: {user_id}): {text}")

        # Обработать команды
        if text.lower() in ['/start', 'начать', 'привет', 'старт']:
            self.send_welcome_message(chat_id)
        else:
            self.send_message(chat_id, "Используйте /start для начала тестирования")

    def handle_message_callback(self, update):
        """Обработать нажатие на кнопку"""
        # В MAX API структура callback: update.callback и update.message
        callback = update.get('callback', {})
        message = update.get('message', {})  # Само сообщение с кнопкой

        user = callback.get('user', {})
        user_id = user.get('user_id')

        # ВАЖНО: chat_id находится в message.recipient.chat_id
        # НО message - это сообщение БОТА, а recipient - это получатель (пользователь)
        # Поэтому chat_id = recipient.chat_id
        recipient = message.get('recipient', {})
        chat_id = recipient.get('chat_id')

        # Получить данные из payload кнопки
        button_payload = callback.get('payload')

        print(f"🔘 Callback от пользователя {user.get('first_name')} (ID: {user_id})")
        print(f"📍 Chat ID: {chat_id}")
        print(f"📦 Payload: {button_payload}")

        if not button_payload:
            print("⚠️  Payload кнопки пустой!")
            return

        if not user_id or not chat_id:
            print(f"⚠️  Не удалось получить user_id ({user_id}) или chat_id ({chat_id})")
            return

        try:
            data = json.loads(button_payload)
            action = data.get('action')

            print(f"✅ Действие: {action}")

            if action == 'start_test':
                self.start_test(user_id, chat_id)
            elif action == 'answer':
                question = data.get('question')
                option = data.get('option')
                criteria = data.get('criteria')
                self.process_answer(user_id, chat_id, question, option, criteria)
            elif action == 'skip':
                question = data.get('question')
                self.skip_question(user_id, chat_id, question)

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка декодирования payload: {e}")

    def handle_bot_started(self, update):
        """Обработать событие bot_started"""
        payload = update.get('payload', {})
        user = payload.get('user', {})
        chat_id = payload.get('chat_id')
        user_id = user.get('user_id')

        if user_id and chat_id:
            # Сохранить пользователя
            self.db.add_or_update_user(
                user_id=user_id,
                chat_id=chat_id,
                username=user.get('username'),
                first_name=user.get('first_name'),
                last_name=user.get('last_name')
            )

            print(f"✅ Новый пользователь: {user_id}")
            self.send_welcome_message(chat_id)

    def process_update(self, update):
        """Обработать одно обновление"""
        # ВАЖНО: В API MAX поле называется 'update_type', а не 'type'!
        update_type = update.get('update_type')

        print(f"🔔 Тип обновления: {update_type}")

        if update_type == 'message_created':
            self.handle_message_created(update)
        elif update_type == 'message_callback':
            self.handle_message_callback(update)
        elif update_type == 'bot_started':
            self.handle_bot_started(update)
        else:
            print(f"⚠️  Неизвестный тип обновления: {update_type}")

    def run(self):
        """Запустить бота"""
        print("=" * 60)
        print("🤖 БОТ ЗАПУЩЕН")
        print("=" * 60)
        print(f"API: {self.api_url}")
        print(f"Токен: {self.token[:20]}...")
        print("=" * 60)
        print("\n⏳ Ожидание обновлений...")
        print("💡 Отправьте боту сообщение в MAX: https://max.ru/id3123232342_bot")
        print()

        iteration = 0
        while True:
            try:
                iteration += 1
                updates = self.get_updates()

                if updates:
                    print(f"\n📬 Получено обновлений: {len(updates)}")
                    for update in updates:
                        self.process_update(update)
                else:
                    # Показываем признаки жизни каждые 10 итераций
                    if iteration % 10 == 0:
                        print(f"⏰ [{iteration}] Бот работает, ожидание сообщений...")

                # Небольшая пауза, чтобы не спамить
                time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n\n🛑 Бот остановлен пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)

if __name__ == '__main__':
    bot = MaxBot()
    bot.run()
