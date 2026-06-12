import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7676835960
CARD_NUMBER = "5168 7500 0000 0000"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}


@app.route('/')
def home():
    return "Bot is live"


def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu")
    )

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в SNOW UC SHOP!",
        reply_markup=markup
    )


# ---------------- CALLBACKS ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    try:
        chat_id = call.message.chat.id

        # главное меню
        if call.data == "buy_menu":

            packs = [
                ("60 UC", "buy_60"), ("120 UC", "buy_120"), ("180 UC", "buy_180"),
                ("325 UC", "buy_325"), ("385 UC", "buy_385"), ("660 UC", "buy_660"),
                ("720 UC", "buy_720"), ("985 UC", "buy_985"), ("1045 UC", "buy_1045"),
                ("1320 UC", "buy_1320"), ("1440 UC", "buy_1440"), ("1800 UC", "buy_1800"),
                ("1920 UC", "buy_1920"), ("2125 UC", "buy_2125"), ("2460 UC", "buy_2460"),
                ("3120 UC", "buy_3120"), ("3850 UC", "buy_3850"), ("4510 UC", "buy_4510"),
                ("5650 UC", "buy_5650"), ("8100 UC", "buy_8100"), ("9900 UC", "buy_9900"),
                ("11950 UC", "buy_11950"), ("16200 UC", "buy_16200")
            ]

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(*[
                types.InlineKeyboardButton(text, callback_data=data)
