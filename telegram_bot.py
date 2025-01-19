import telebot
from extensions import db
from models import BotMessage, Fact   # Импорт модели для сохранения сообщений
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
    
# Глобальный словарь для отслеживания активных потоков
active_threads = {}

def send_random_fact_from_db(chat_id):
    print("Запуск потока для отправки фактов...")
    with app.app_context():
        while active_threads.get(chat_id, False):  # Проверяем состояние флага
            try:
                facts = Fact.query.all()
                print(f"Найдено фактов: {len(facts)}")
                if facts:
                    random_fact = random.choice(facts).text
                    print(f"Отправка факта: {random_fact}")
                    bot.send_message(chat_id, f'Интересный факт: {random_fact}')
                time.sleep(10)  # Интервал между отправкой фактов
            except Exception as e:
                print(f"Ошибка при чтении фактов из базы данных: {e}")
                break
    print(f"Поток для чата {chat_id} остановлен.")

# Обработчик команды /facts
@bot.message_handler(commands=['facts'])
def facts_message(message):
    chat_id = message.chat.id
    if active_threads.get(chat_id, False):
        bot.reply_to(message, 'Отправка фактов уже запущена! Чтобы остановить, напишите /stop.')
    else:
        active_threads[chat_id] = True  # Устанавливаем флаг для данного чата
        threading.Thread(target=send_random_fact_from_db, args=(chat_id,)).start()
        bot.reply_to(message, 'Я начну присылать тебе интересные факты с интервалом в 10 секунд! Для того чтобы остановить отправку напиши /stop')

# Обработчик команды /stop
@bot.message_handler(commands=['stop'])
def stop_message(message):
    chat_id = message.chat.id
    if active_threads.get(chat_id, False):
        active_threads[chat_id] = False  # Устанавливаем флаг в False, чтобы остановить поток
        bot.reply_to(message, 'Отправка фактов остановлена! Спасибо, что использовали меня.')
    else:
        bot.reply_to(message, 'Отправка фактов не активна.')

# Запуск бота в отдельном потоке
def run_bot():
    with app.app_context():
        db.create_all()  # Создание таблиц, если они не существуют
    bot.polling(none_stop=True)

if __name__ == "__main__":
    run_bot()
