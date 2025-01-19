import telebot
from extensions import db
from models import BotMessage  # Импорт модели для сохранения сообщений
import threading
import random
import time
from flask import Flask

# Telegram Bot Token
BOT_TOKEN = "8178279080:AAFGRlo8wjW16NIkAyp0DAUT8RvdyvTExxg"
bot = telebot.TeleBot(BOT_TOKEN)

# Flask приложение для доступа к контексту базы данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://047084354_zvir:Arti2005@mysql.j1007852.myjino.ru:3306/j1007852_237_zvir"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Приветственные фразы
random_phrases = {
    1: "Привет! Хорошо, что ты здесь!",
    2: "Добро пожаловать! Давай вместе узнавать факты",
    3: "Привет! Не забывай, знания - сила!",
}

# Функция для сохранения сообщения в базу данных
def save_message_to_db(message):
    with app.app_context():
        new_message = BotMessage(
            user_id=message.from_user.id,
            username=message.from_user.username,
            chat_id=message.chat.id,
            message_text=message.text,
            message_type='text' if message.content_type == 'text' else message.content_type
        )
        db.session.add(new_message)
        db.session.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    save_message_to_db(message)  # Сохранение команды в базу данных
    random_start_msg = random.choice(list(random_phrases.values()))
    bot.reply_to(message, random_start_msg)

# Отправка случайных фактов из базы данных
def send_random_fact_from_db(chat_id):
    with app.app_context():
        while True:
            try:
                facts = BotMessage.query.filter(BotMessage.message_type == 'fact').all()
                if facts:
                    random_fact = random.choice(facts).message_text
                    bot.send_message(chat_id, f'Интересный факт: {random_fact}')
                time.sleep(10)
            except Exception as e:
                print(f"Ошибка при чтении фактов из базы данных: {e}")
                break

# Обработчик команды /facts
@bot.message_handler(commands=['facts'])
def facts_message(message):
    save_message_to_db(message)  # Сохранение команды в базу данных
    chat_id = message.chat.id
    threading.Thread(target=send_random_fact_from_db, args=(chat_id,)).start()
    bot.reply_to(message, 'Я начну присылать тебе интересные факты!')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    save_message_to_db(message)  # Сохранение каждого сообщения в базу данных
    if message.text.lower() == "стоп":
        bot.reply_to(message, "Остановлено! Спасибо за использование.")
    else:
        response = random.choice(["Ты угадал!", "Попробуй снова!", "Интересная попытка!"])
        bot.reply_to(message, response)

# Запуск бота в отдельном потоке
def run_bot():
    with app.app_context():
        db.create_all()  # Создание таблиц, если они не существуют
    bot.polling(none_stop=True)

if __name__ == "__main__":
    run_bot()
