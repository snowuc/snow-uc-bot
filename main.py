import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy_menu":
        bot.send_message(chat_id, "💎 Выберите пак:")
    elif call.data.startswith("buy_"):
        bot.send_message(chat_id, "✅ Пак выбран! Напишите ID (на 5).")

@bot.message_handler(func=lambda message: True)
def handle_id(message):
    if message.text.startswith('5'):
        bot.reply_to(message, "✅ ID принят.")
    else:
        bot.reply_to(message, "❌ Ошибка: ID на 5.")

if __name__ == '__main__':
    Thread(target=run_server).start()
    bot.infinity_polling()
    
