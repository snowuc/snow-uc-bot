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
def home(): return "Bot is running"

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
    bot.answer_callback_query(call.id) # Убирает "часики" с кнопок

    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        packs = [("60 UC", "buy_60"), ("120 UC", "buy_120"), ("325 UC", "buy_325"), ("660 UC", "buy_660")]
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=p[1]) for p in packs])
        bot.edit_message_text("💎 Выберите пак:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        user_data[chat_id] = {"pack": call.data.split("_")[1]}
        bot.edit_message_text("Введите ID (начинается на 5):", chat_id, call.message.message_id)

    elif call.data == "confirm_yes":
        bot.edit_message_text("💳 Карта: <code>5168 7500 0000 0000</code>. Пришлите чек.", chat_id, call.message.message_id, parse_mode="HTML")

    elif call.data == "confirm_no":
        if chat_id in user_data: del user_data[chat_id]
        bot.edit_message_text("❌ Отменено. Напишите /start", chat_id, call.message.message_id)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    chat_id = message.chat.id
    # Если пользователь ввел ID
    if chat_id in user_data and "id" not in user_data[chat_id]:
        if message.text.startswith('5'):
            user_data[chat_id]["id"] = message.text
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ Да", callback_data="confirm_yes"), types.InlineKeyboardButton("❌ Нет", callback_data="confirm_no"))
            try:
                bot.send_photo(chat_id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                               caption=f"Ваш ID: {message.text}. Верно?", reply_markup=markup)
            except:
                bot.send_message(chat_id, f"Ваш ID: {message.text}. Верно?", reply_markup=markup)
        else:
            bot.reply_to(message, "❌ Ошибка: ID должен начинаться на 5.")
    # Если прислал фото чека
    elif message.content_type == 'photo' and chat_id in user_data and "id" in user_data[chat_id]:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 ЗАКАЗ!\nОт: {message.chat.id}\nID: {user_data[chat_id]['id']}\nПак: {user_data[chat_id]['pack']}")
        bot.reply_to(message, "✅ Чек получен!")
        del user_data[chat_id]

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
