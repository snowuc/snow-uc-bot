import telebot
import os
from flask import Flask
from threading import Thread

# Настройка
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Чтобы Render видел, что сайт работает (отсутствие этой части иногда вызывает сбой)
@app.route('/')
def home():
    return "Bot is alive"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Обработка /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=markup)

# Обработка нажатий
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "buy_menu":
        bot.send_message(call.message.chat.id, "💎 Выберите пак: (например, 60 UC - 41₴)")
    elif call.data.startswith("buy_"):
        bot.send_message(call.message.chat.id, "✅ Пак выбран. Напишите ваш ID (начинается на 5):")

# Обработка ID
@bot.message_handler(func=lambda message: message.text.startswith('5'))
def handle_id(message):
    bot.reply_to(message, "✅ ID принят. Ожидайте подтверждения.")

if __name__ == '__main__':
    # Запуск Flask сервера в фоне
    Thread(target=run).start()
    # Запуск бота
    bot.infinity_polling()
