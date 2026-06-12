import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# НАСТРОЙКИ
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"  # Твой ID, на который будут приходить уведомления
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище: id пользователя -> {pack, id}
user_data = {}

@app.route('/')
def home(): return "Бот работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Команда старт
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
        packs = [("60 UC", "buy_60"), ("120 UC", "buy_120"), ("180 UC", "buy_180"), 
                 ("325 UC", "buy_325"), ("385 UC", "buy_385"), ("660 UC", "buy_660"),
                 ("720 UC", "buy_720"), ("985 UC", "buy_985"), ("1045 UC", "buy_1045"),
                 ("1320 UC", "buy_1320"), ("1440 UC", "buy_1440"), ("1800 UC", "buy_1800"),
                 ("1920 UC", "buy_1920"), ("2125 UC", "buy_2125"), ("2460 UC", "buy_2460"),
                 ("3120 UC", "buy_3120"), ("3850 UC", "buy_3850"), ("4510 UC", "buy_4510"),
                 ("5650 UC", "buy_5650"), ("8100 UC", "buy_8100"), ("9900 UC", "buy_9900"),
                 ("11950 UC", "buy_11950"), ("16200 UC", "buy_16200")]
        buttons = [types.InlineKeyboardButton(text=p[0], callback_data=p[1]) for p in packs]
        markup.add(*buttons)
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="💎 Выберите пак:", reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        user_data[chat_id] = {"pack": call.data.split("_")[1]}
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "Введите ваш игровой ID (начинается на 5):")

    elif call.data == "confirm_yes":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text="💳 Переведите на карту: <code>5168 7500 0000 0000</code>\n\nПришлите чек (фото).", parse_mode="HTML")

    elif call.data == "confirm_no":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Введите ID заново:")
        if chat_id in user_data: del user_data[chat_id]

# Ввод ID
@bot.message_handler(func
                     
