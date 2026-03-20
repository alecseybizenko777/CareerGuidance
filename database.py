# -*- coding: utf-8 -*-
import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Создать соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализация таблиц базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица вопросов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_order INTEGER NOT NULL,
                option1_text TEXT NOT NULL,
                option1_criteria TEXT NOT NULL,
                option2_text TEXT NOT NULL,
                option2_criteria TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица ПОО
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS educational_organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                criteria_text TEXT NOT NULL,
                criteria_list TEXT NOT NULL,
                logo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                chat_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица результатов тестирования
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                current_question INTEGER DEFAULT 0,
                score_human INTEGER DEFAULT 0,
                score_nature INTEGER DEFAULT 0,
                score_tech INTEGER DEFAULT 0,
                score_sign INTEGER DEFAULT 0,
                score_art INTEGER DEFAULT 0,
                is_completed BOOLEAN DEFAULT 0,
                answers_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ База данных инициализирована")

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ===

    def add_or_update_user(self, user_id, chat_id, username=None, first_name=None, last_name=None):
        """Добавить или обновить пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, chat_id, username, first_name, last_name, last_activity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, chat_id, username, first_name, last_name, datetime.now()))

        conn.commit()
        conn.close()

    def get_user(self, user_id):
        """Получить пользователя по user_id"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()

        conn.close()
        return dict(user) if user else None

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ВОПРОСАМИ ===

    def add_question(self, order, opt1_text, opt1_criteria, opt2_text, opt2_criteria):
        """Добавить вопрос"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO questions (question_order, option1_text, option1_criteria, option2_text, option2_criteria)
            VALUES (?, ?, ?, ?, ?)
        ''', (order, opt1_text, opt1_criteria, opt2_text, opt2_criteria))

        conn.commit()
        conn.close()

    def get_all_questions(self):
        """Получить все вопросы"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM questions ORDER BY question_order')
        questions = cursor.fetchall()

        conn.close()
        return [dict(q) for q in questions]

    def get_question_by_order(self, order):
        """Получить вопрос по номеру"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM questions WHERE question_order = ?', (order,))
        question = cursor.fetchone()

        conn.close()
        return dict(question) if question else None

    def get_total_questions_count(self):
        """Получить общее количество вопросов"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM questions')
        result = cursor.fetchone()

        conn.close()
        return result['count'] if result else 0

    def update_question(self, question_id, order, opt1_text, opt1_criteria, opt2_text, opt2_criteria):
        """Обновить вопрос"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE questions
            SET question_order = ?, option1_text = ?, option1_criteria = ?,
                option2_text = ?, option2_criteria = ?
            WHERE id = ?
        ''', (order, opt1_text, opt1_criteria, opt2_text, opt2_criteria, question_id))

        conn.commit()
        conn.close()

    def delete_question(self, question_id):
        """Удалить вопрос"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))

        conn.commit()
        conn.close()

    def get_question_by_id(self, question_id):
        """Получить вопрос по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
        question = cursor.fetchone()

        conn.close()
        return dict(question) if question else None

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПОО ===

    def add_organization(self, name, url, criteria_text, criteria_list, logo_path=None):
        """Добавить ПОО"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO educational_organizations (name, url, criteria_text, criteria_list, logo_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, url, criteria_text, json.dumps(criteria_list), logo_path))

        conn.commit()
        conn.close()

    def get_all_organizations(self):
        """Получить все ПОО"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM educational_organizations')
        orgs = cursor.fetchall()

        conn.close()
        return [dict(org) for org in orgs]

    def get_organizations_by_criteria(self, criteria_list):
        """Получить ПОО по критериям"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM educational_organizations')
        all_orgs = cursor.fetchall()

        matching_orgs = []
        for org in all_orgs:
            org_criteria = json.loads(org['criteria_list'])
            # Если хотя бы один критерий совпадает
            if any(c in criteria_list for c in org_criteria):
                matching_orgs.append(dict(org))

        conn.close()
        return matching_orgs

    # === МЕТОДЫ ДЛЯ РАБОТЫ С РЕЗУЛЬТАТАМИ ТЕСТОВ ===

    def start_test(self, user_id):
        """Начать новый тест"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO test_results (user_id, answers_json)
            VALUES (?, ?)
        ''', (user_id, json.dumps([])))

        test_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return test_id

    def get_active_test(self, user_id):
        """Получить активный тест пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM test_results
            WHERE user_id = ? AND is_completed = 0
            ORDER BY started_at DESC
            LIMIT 1
        ''', (user_id,))

        test = cursor.fetchone()

        conn.close()
        return dict(test) if test else None

    def update_test_answer(self, test_id, question_num, selected_option, criteria):
        """Обновить ответ на вопрос"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получить текущий тест
        cursor.execute('SELECT * FROM test_results WHERE id = ?', (test_id,))
        test = cursor.fetchone()

        if not test:
            conn.close()
            return False

        # Обновить ответы
        answers = json.loads(test['answers_json']) if test['answers_json'] else []
        answers.append({
            'question': question_num,
            'selected': selected_option,
            'criteria': criteria
        })

        # Обновить баллы
        score_field = f'score_{criteria.lower()}'
        new_score = test[score_field] + 1

        cursor.execute(f'''
            UPDATE test_results
            SET {score_field} = ?,
                current_question = ?,
                answers_json = ?
            WHERE id = ?
        ''', (new_score, question_num + 1, json.dumps(answers), test_id))

        conn.commit()
        conn.close()
        return True

    def complete_test(self, test_id):
        """Завершить тест"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_results
            SET is_completed = 1,
                completed_at = ?
            WHERE id = ?
        ''', (datetime.now(), test_id))

        conn.commit()
        conn.close()

    def get_test_results(self, test_id):
        """Получить результаты теста"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM test_results WHERE id = ?', (test_id,))
        test = cursor.fetchone()

        conn.close()
        return dict(test) if test else None

    # === МЕТОДЫ ДЛЯ СТАТИСТИКИ ===

    def get_statistics(self):
        """Получить общую статистику"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Общее количество пользователей
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']

        # Общее количество тестов
        cursor.execute('SELECT COUNT(*) as count FROM test_results')
        total_tests = cursor.fetchone()['count']

        # Завершенные тесты
        cursor.execute('SELECT COUNT(*) as count FROM test_results WHERE is_completed = 1')
        completed_tests = cursor.fetchone()['count']

        # Топ критериев
        cursor.execute('''
            SELECT
                AVG(score_human) as avg_human,
                AVG(score_nature) as avg_nature,
                AVG(score_tech) as avg_tech,
                AVG(score_sign) as avg_sign,
                AVG(score_art) as avg_art
            FROM test_results WHERE is_completed = 1
        ''')
        avg_scores = cursor.fetchone()

        conn.close()

        return {
            'total_users': total_users,
            'total_tests': total_tests,
            'completed_tests': completed_tests,
            'incomplete_tests': total_tests - completed_tests,
            'avg_scores': dict(avg_scores) if avg_scores else {}
        }
