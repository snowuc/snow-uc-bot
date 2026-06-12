import telebot
from telebot import types
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Бот активен!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960

bot = telebot.TeleBot(TOKEN)

# Функция меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📋 Прайс-лист"), types.KeyboardButton("💰 Купить UC"))
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Добро пожаловать в SNOW UC SHOP ❄️", reply_markup=main_menu())

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "📋 Прайс-лист":
        bot.send_message(message.chat.id, "Прайс-лист нашего магазина...")
    elif message.text == "💰 Купить UC":
        msg = bot.send_message(message.chat.id, "Введите ваш PUBG ID и кол-во UC:")
        bot.register_next_step_handler(msg, process_order)

def process_order(message):
    bot.send_message(message.chat.id, "✅ Заказ принят!")
    bot.send_message(ADMIN_ID, f"🚨 Новый заказ от {message.from_user.username or message.from_user.first_name}: {message.text}")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
