import telebot
import os
from flask import Flask
from threading import Thread
from telebot import types

# Прямое указание токена для запуска в Pydroid
TOKEN = '8986699759:AAHc-RqjhrDM9kDoQmE2qT5ONnOWZ_fSSLk'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "<b>✨ Добро пожаловать в SNOW UC SHOP!</b>", 
                     reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy_menu":
        bot.send_message(chat_id, "💎 Выберите пак.")
    elif call.data == "pay_monobank":
        bot.send_message(chat_id, "💳 Карта: <code>5168 7500 0000 0000</code>", parse_mode="HTML")

if __name__ == '__main__':
    Thread(target=run_server).start()
    bot.polling(none_stop=True)
