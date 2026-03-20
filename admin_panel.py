# -*- coding: utf-8 -*-
"""
Веб админ-панель для управления ботом
"""
import sys
import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from database import Database
from config import SECRET_KEY, FLASK_HOST, FLASK_PORT, CRITERIA
import config

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

db = Database()

@app.route('/')
def index():
    """Главная страница"""
    stats = db.get_statistics()
    return render_template('index.html', stats=stats, criteria=CRITERIA)

@app.route('/api/statistics')
def get_statistics():
    """API: Получить статистику"""
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/questions')
def get_questions():
    """API: Получить все вопросы"""
    questions = db.get_all_questions()
    return jsonify(questions)

@app.route('/api/organizations')
def get_organizations():
    """API: Получить все ПОО"""
    orgs = db.get_all_organizations()
    return jsonify(orgs)

@app.route('/api/test_results')
def get_test_results():
    """API: Получить все результаты тестов"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            tr.*,
            u.username,
            u.first_name,
            u.last_name
        FROM test_results tr
        LEFT JOIN users u ON tr.user_id = u.user_id
        WHERE tr.is_completed = 1
        ORDER BY tr.completed_at DESC
    ''')

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(results)

@app.route('/api/settings')
def get_settings():
    """API: Получить настройки"""
    return jsonify({
        'min_score_to_show': config.MIN_SCORE_TO_SHOW,
        'poo_selection_mode': config.POO_SELECTION_MODE,
        'allow_skip_questions': config.ALLOW_SKIP_QUESTIONS
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """API: Обновить настройки"""
    data = request.get_json()
    import re

    # Обновить значение в config.py
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'min_score_to_show' in data:
        new_value = int(data['min_score_to_show'])
        content = re.sub(
            r'MIN_SCORE_TO_SHOW\s*=\s*\d+',
            f'MIN_SCORE_TO_SHOW = {new_value}',
            content
        )
        config.MIN_SCORE_TO_SHOW = new_value

    if 'poo_selection_mode' in data:
        new_value = data['poo_selection_mode']
        content = re.sub(
            r"POO_SELECTION_MODE\s*=\s*['\"].*?['\"]",
            f"POO_SELECTION_MODE = '{new_value}'",
            content
        )
        config.POO_SELECTION_MODE = new_value

    if 'allow_skip_questions' in data:
        new_value = bool(data['allow_skip_questions'])
        content = re.sub(
            r'ALLOW_SKIP_QUESTIONS\s*=\s*(True|False)',
            f'ALLOW_SKIP_QUESTIONS = {new_value}',
            content
        )
        config.ALLOW_SKIP_QUESTIONS = new_value

    # Сохранить изменения в файл
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return jsonify({'success': True, 'message': 'Настройки обновлены'})

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """API: Получить конкретный вопрос"""
    question = db.get_question_by_id(question_id)
    if question:
        return jsonify(question)
    return jsonify({'error': 'Вопрос не найден'}), 404

@app.route('/api/questions', methods=['POST'])
def create_question():
    """API: Создать новый вопрос"""
    data = request.get_json()

    try:
        db.add_question(
            order=int(data['question_order']),
            opt1_text=data['option1_text'],
            opt1_criteria=data['option1_criteria'],
            opt2_text=data['option2_text'],
            opt2_criteria=data['option2_criteria']
        )
        return jsonify({'success': True, 'message': 'Вопрос создан'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """API: Обновить вопрос"""
    data = request.get_json()

    try:
        db.update_question(
            question_id=question_id,
            order=int(data['question_order']),
            opt1_text=data['option1_text'],
            opt1_criteria=data['option1_criteria'],
            opt2_text=data['option2_text'],
            opt2_criteria=data['option2_criteria']
        )
        return jsonify({'success': True, 'message': 'Вопрос обновлен'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """API: Удалить вопрос"""
    try:
        db.delete_question(question_id)
        return jsonify({'success': True, 'message': 'Вопрос удален'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("🌐 АДМИН-ПАНЕЛЬ ЗАПУЩЕНА")
    print("=" * 60)
    print(f"URL: http://{FLASK_HOST}:{FLASK_PORT}")
    print("=" * 60)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
