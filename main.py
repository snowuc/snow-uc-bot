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

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy_menu":
        # ... (здесь твой старый код с кнопками паков) ...
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="💎 Выберите пак:", reply_markup=markup)
    elif call.data.startswith("buy_"):
        photo_url = "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg"
        caption = "✅ Пак выбран! Напишите ваш ID (начинается на 5)."
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_photo(chat_id, photo_url, caption=caption)

@bot.message_handler(func=lambda message: True)
def handle_id(message):
    if message.text.startswith('5'):
        bot.reply_to(message, "✅ ID принят.")
    else:
        bot.reply_to(message, "❌ ID должен начинаться на 5.")

if __name__ == '__main__':
    Thread(target=run_server).start()
    bot.infinity_polling()
    
