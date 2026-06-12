import telebot
import os
from flask import Flask
from threading import Thread
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- БЛОК 1: Web-сервер для Render ---
@app.route('/')
def home(): return "Бот активен"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- БЛОК 2: Меню и логика ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Паки
        packs = [("60 UC", "buy_60"), ("120 UC", "buy_120"), ("325 UC", "buy_325"), ("660 UC", "buy_660")]
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=p[1]) for p in packs])
        bot.edit_message_text("💎 Выберите пак:", call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        bot.edit_message_text("✅ Пак выбран. Напишите ваш ID (начинается на 5):", call.message.chat.id, call.message.message_id)

# --- БЛОК 3: ID и Фото ---
@bot.message_handler(func=lambda message: message.text.startswith('5'))
def handle_id(message):
    bot.reply_to(message, "✅ ID принят! Отправьте скриншот чека.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 Новый чек от {message.chat.id}")
    bot.reply_to(message, "✅ Чек получен, ожидайте!")

if __name__ == '__main__':
    Thread(target=run).start()
    bot.infinity_polling()
