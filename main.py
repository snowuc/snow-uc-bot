import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# Настройка
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Flask нужен для Render, чтобы он не закрывал бота
@app.route('/')
def home():
    return "Бот работает!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=markup)

# Обработка всех нажатий и сообщений
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        packs = [
            ("60 UC - 41₴", "buy_60"), ("120 UC - 82₴", "buy_120"),
            ("180 UC - 123₴", "buy_180"), ("325 UC - 215₴", "buy_325"),
            ("385 UC - 250₴", "buy_385"), ("660 UC - 400₴", "buy_660"),
            ("720 UC - 440₴", "buy_720"), ("985 UC - 615₴", "buy_985"),
            ("1045 UC - 655₴", "buy_1045"), ("1320 UC - 790₴", "buy_1320"),
            ("1440 UC - 870₴", "buy_1440"), ("1800 UC - 1020₴", "buy_1800"),
            ("1920 UC - 1100₴", "buy_1920"), ("2125 UC - 1205₴", "buy_2125"),
            ("2460 UC - 1390₴", "buy_2460"), ("3120 UC - 1785₴", "buy_3120"),
            ("3850 UC - 2000₴", "buy_3850"), ("4510 UC - 2380₴", "buy_4510"),
            ("5650 UC - 3030₴", "buy_5650"), ("8100 UC - 3900₴", "buy_8100"),
            ("9900 UC - 4920₴", "buy_9900"), ("11950 UC - 5900₴", "buy_11950"),
            ("16200 UC - 7800₴", "buy_16200")
        ]
        buttons = [types.InlineKeyboardButton(text=p[0], callback_data=p[1]) for p in packs]
        markup.add(*buttons)
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text="💎 Выберите пак для покупки:", reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        photo_url = "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg"
        caption_text = "✅ Пак успешно выбран!\n💳 Оплатите на карту 5168 7500 0000 0000 и пришлите ваш ID (должен начинаться на 5)."
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_photo(chat_id, photo_url, caption=caption_text)

@bot.message_handler(func=lambda message: True)
def handle_id(message):
    if message.text.startswith('5'):
        bot.reply_to(message, "✅ Спасибо! ID принят, ожидайте.")
    else:
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться на 5.")

if __name__ == '__main__':
    Thread(target=run_server).start()
    bot.infinity_polling()
    
