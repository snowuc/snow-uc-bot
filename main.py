import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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
    bot.send_message(message.chat.id, "👋 Добро пожаловать! Нажми кнопку ниже:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        # ВСЕ ПАКИ ЗДЕСЬ
        packs = [("60 UC", "buy_60"), ("120 UC", "buy_120"), ("325 UC", "buy_325"), ("660 UC", "buy_660"), 
                 ("720 UC", "buy_720"), ("1800 UC", "buy_1800"), ("3850 UC", "buy_3850"), ("8100 UC", "buy_8100")]
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=p[1]) for p in packs])
        bot.edit_message_text("💎 Выбери пак:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        user_data[chat_id] = {"pack": call.data.split("_")[1]}
        bot.edit_
