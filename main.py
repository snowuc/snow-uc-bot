import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Храним только ID пользователя, чтобы знать, что он в процессе заказа
waiting_for_id = {}

@app.route('/')
def home(): return "Bot is live"

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
    
    # 1. Меню паков
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        packs = [("60 UC", "60"), ("120 UC", "120"), ("325 UC", "325"), ("660 UC", "660"), 
                 ("720 UC", "720"), ("1800 UC", "1800"), ("3850 UC", "3850"), ("8100 UC", "8100")]
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=f"pack_{p[1]}") for p in packs])
        bot.edit_message_text("💎 Выберите пак:", chat_id, call.message.message_id, reply_markup=markup)
    
    # 2. Выбран конкретный пак (сохраняем выбор в данные кнопки)
    elif call.data.startswith("pack_"):
        pack_value = call.data.split("_")[1]
        waiting_for_id[chat_id] = {"pack": pack_value}
        bot.edit_message_text(f"✅ Выбрано: {pack_value} UC. Введите ID (начинается на 5):", chat_id, call.message.message_id)

    # 3. Подтверждение
    elif call.data == "confirm":
        bot.edit_message_text("💳 Карта: <code>5168 7500 0000 0000</code>.\n\n📸 Пришлите скриншот чека.", chat_id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.chat.id in waiting_for_id and "id" not in waiting_for_id[m.chat.id])
def handle_id(message):
    if message.text.startswith('5'):
        waiting_for_id[message.chat.id]["id"] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        
        # Отправляем фото и кнопку
        try:
            bot.send_photo(message.chat.id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                           caption=f"Ваш ID: {message.text}. Верно?", reply_markup=markup)
        except:
            bot.send_message(message.chat.id, f"ID: {message.text}. Нажмите кнопку для оплаты:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться с 5.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id in waiting_for_id and "id" in waiting_for_id[message.chat.id]:
        data = waiting_for_id[message.chat.id]
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                       caption=f"🔔 НОВЫЙ ЗАКАЗ!\nКлиент: @{message.from_user.username or message.chat.id}\nID: {data['id']}\nПак: {data['pack']} UC")
        bot.reply_to(message, "✅ Чек получен! Ожидайте зачисления.")
        del waiting_for_id[message.chat.id]

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
