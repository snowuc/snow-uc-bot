import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот активен!"

# Главное меню
def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 Прайс-лист", callback_data="price"))
    markup.add(types.InlineKeyboardButton("💰 Купить UC", callback_data="buy"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я твой помощник SNOW UC SHOP ❄️", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "price":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="🔥 **Прайс-лист:**\n60 UC - 45 грн\n325 UC - 210 грн", reply_markup=get_main_menu())
    
    elif call.data == "buy":
        msg = bot.send_message(call.message.chat.id, "📩 Введите ваш PUBG ID и количество UC одной строкой:")
        bot.register_next_step_handler(msg, process_buy)

def process_buy(message):
    user_text = message.text
    # Отправка админу
    try:
        bot.send_message(ADMIN_ID, f"🚨 **Новый заказ!**\n👤 От: @{message.from_user.username}\n📦 Данные: {user_text}")
        bot.send_message(message.chat.id, "✅ **Ваш заказ успешно отправлен!** Администратор скоро свяжется с вами.")
    except Exception:
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте снова.")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
