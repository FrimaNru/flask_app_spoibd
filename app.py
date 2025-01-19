import threading
from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from extensions import db
from models import Fact, Admin, BotMessage
from telegram_bot import run_bot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://047084354_zvir:Arti2005@mysql.j1007852.myjino.ru:3306/j1007852_237_zvir"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "e2c4b9274f1e7b6a8b9f0d4f7c3a9d12"
db.init_app(app)

# Создание блюпринта для статистики
statistics_blueprint = Blueprint('statistics', __name__, url_prefix='/statistics')

@statistics_blueprint.route('/')
def statistics():
    # Получение статистики для вкладок
    daily_data = db.session.query(
        db.func.date(BotMessage.timestamp),
        db.func.count(BotMessage.id)
    ).group_by(db.func.date(BotMessage.timestamp)).all()

    user_data = db.session.query(
        BotMessage.username,
        db.func.count(BotMessage.id)
    ).group_by(BotMessage.username).all()

    command_data = db.session.query(
        BotMessage.message_text,
        db.func.count(BotMessage.id)
    ).filter(BotMessage.message_text.startswith('/')).group_by(BotMessage.message_text).all()

    # Общая информация
    total_messages = len(daily_data)
    user_count = len(user_data)
    command_count = len(command_data)
    user = session.get('user')

    return render_template(
        'statistics.html',
        daily_data=daily_data,
        user_data=user_data,
        command_data=command_data,
        total_messages=total_messages,
        user_count=user_count,
        command_count=command_count,
        user=user
    )


@statistics_blueprint.route('/daily')
def daily_statistics():
    # Пример обработки данных для статистики по дням
    data = db.session.query(
        db.func.date(BotMessage.timestamp),
        db.func.count(BotMessage.id)
    ).group_by(db.func.date(BotMessage.timestamp)).all()
    return jsonify(data)

@statistics_blueprint.route('/users')
def user_statistics():
    # Пример обработки данных для статистики по пользователям
    data = db.session.query(
        BotMessage.username,
        db.func.count(BotMessage.id)
    ).group_by(BotMessage.username).all()
    return jsonify(data)

@statistics_blueprint.route('/commands')
def command_statistics():
    # Пример обработки данных для статистики по командам
    data = db.session.query(
        BotMessage.message_text,
        db.func.count(BotMessage.id)
    ).filter(BotMessage.message_text.startswith('/')).group_by(BotMessage.message_text).all()
    return jsonify(data)

# API маршрут для статистики (добавлен)
@app.route('/api/statistics')
def api_statistics():
    # Пример обработки данных для API статистики
    messages = BotMessage.query.all()
    data = {
        'total_messages': len(messages),
        'user_count': db.session.query(BotMessage.username).distinct().count(),
        'command_count': db.session.query(BotMessage.message_text).filter(BotMessage.message_text.startswith('/')).count()
    }
    return jsonify(data)

# Регистрация блюпринта
app.register_blueprint(statistics_blueprint)

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['user'] = {'username': admin.username, 'role': admin.role}
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if Admin.query.filter_by(username=username).first():
            flash('Логин уже занят!', 'danger')
        else:
            new_admin = Admin(username=username, password=password, role=role)
            db.session.add(new_admin)
            db.session.commit()
            flash('Вы успешно зарегистрировались!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/facts', methods=['GET', 'POST'])
def facts():
    if request.method == 'POST':
        fact_text = request.form.get('fact_text')
        if fact_text:
            new_fact = Fact(text=fact_text)
            db.session.add(new_fact)
            db.session.commit()
            return redirect(url_for('facts'))
    all_facts = Fact.query.all()
    user = session.get('user')
    return render_template('facts.html', facts=all_facts, user=user)

@app.route('/delete_fact/<string:fact_id>', methods=['POST'])
def delete_fact(fact_id):
    fact_to_delete = Fact.query.get(fact_id)
    if fact_to_delete:
        db.session.delete(fact_to_delete)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

if __name__ == "__main__":
    # Создаем поток для запуска бота
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Устанавливаем поток как демонический
    bot_thread.start()

    # Запускаем Flask
    with app.app_context():
        db.create_all()  # Убеждаемся, что таблицы созданы
    app.run(debug=True)
