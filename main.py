import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище временных данных
user_data = {}

@app.route('/')
def home(): return "Бот работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Все 23 пака
        packs = [("60 UC", "buy_60"), ("120 UC", "buy_120"), ("180 UC", "buy_180"), ("325 UC", "buy_325"), 
                 ("385 UC", "buy_385"), ("660 UC", "buy_660"), ("720 UC", "buy_720"), ("985 UC", "buy_985"), 
                 ("1045 UC", "buy_1045"), ("1320 UC", "buy_1320"), ("1440 UC", "buy_1440"), ("1800 UC", "buy_1800"), 
                 ("1920 UC", "buy_1920"), ("2125 UC", "buy_2125"), ("2460 UC", "buy_2460"), ("3120 UC", "buy_3120"), 
                 ("3850 UC", "buy_3850"), ("4510 UC", "buy_4510"), ("5650 UC", "buy_5650"), ("8100 UC", "buy_
