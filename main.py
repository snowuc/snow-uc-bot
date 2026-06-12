import telebot
from telebot import types
import os
from flask import Flask, send_from_directory
from threading import Thread

TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960
WEB_APP_URL = 'https://snow-uc-bot.onrender.com/index.html'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_orders = {}

@app.route('/')
def home(): return "Бот работает!"

@app.route('/index.html')
def serve_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, 'index.html')


def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Открыть магазин", web_app=types.WebAppInfo(url=WEB_APP_URL)))
    bot.send_message(message.chat.id, "✨ Добро пожаловать! Нажми кнопку ниже:", reply_markup=markup)

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    chat_id = message.chat.id
    user_orders[chat_id] = {'amount': message.web_app_data.data}
    bot.send_message(chat_id, f"✅ Выбрано: {message.web_app_data.data}. Введите PUBG ID:")
    bot.register_next_step_handler(message, lambda m: get_pubg_id(m))

def get_pubg_id(message):
    user_orders[message.chat.id]['pubg_id'] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Оплатить", callback_data="pay"))
    bot.send_message(message.chat.id, "✅ ID принят. Нажмите для оплаты.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "pay")
def pay(call):
    bot.edit_message_text("💳 Карта для оплаты: 5168 7500 0000 0000. Отправьте скрин чека сюда.", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Чек отправлен!")

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
