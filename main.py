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
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=p[1]) for p in packs])
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
        if chat_id in user_data and "id" in user_data[chat_id]: del user_data[chat_id]["id"]

@bot.message_handler(func=lambda message: message.chat.id in user_data and "id" not in user_data[message.chat.id])
def handle_id(message):
    if message.text.startswith('5'):
        user_data[message.chat.id]["id"] = message.text
        photo_url = "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Да", callback_data="confirm_yes"), 
                   types.InlineKeyboardButton("Нет", callback_data="confirm_no"))
        bot.send_photo(message.chat.id, photo_url, caption=f"Ваш ID: {message.text}. Верно?", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться на 5.")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    if message.chat.id in user_data and "id" in user_data[message.chat.id]:
        data = user_data[message.chat.id]
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"🔔 Заказ!\nID: {data['id']}\nПак: {data['pack']} UC")
        bot.reply_to(message, "✅ Чек получен! Ожидайте зачисления.")
        del user_data[message.chat.id]

if __name__ == '__main__':
    Thread(target=run_server).start()
    bot.infinity_polling()
    
