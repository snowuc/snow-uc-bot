import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960

bot = telebot.TeleBot(TOKEN)

# Веб-сервер для Render
app = Flask(__name__)
@app.route('/')
def home():
    return "Бот активен!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Главное меню с Inline-кнопками
def get_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 Прайс-лист", callback_data="price"))
    markup.add(types.InlineKeyboardButton("💰 Купить UC", callback_data="buy"))
    markup.add(types.InlineKeyboardButton("ℹ️ О нас", callback_data="about"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 
                     "❄️ **SNOW UC SHOP**\n\nДобро пожаловать! Выберите нужный раздел в меню ниже:", 
                     parse_mode="Markdown", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "price":
        text = ("🔥 **ПРАЙС-ЛИСТ**\n\n"
                "🔹 60+5 UC — 45 грн\n"
                "🔹 325+30 UC — 210 грн\n"
                "🔹 660+60 UC — 415 грн\n"
                "--- Для заказа вернитесь в меню ---")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=text, parse_mode="Markdown", reply_markup=get_main_menu())
    
    elif call.data == "about":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="❄️ **SNOW UC SHOP** — твой надежный магазин валюты PUBG Mobile. Работаем быстро, безопасно и с лучшими ценами!", 
                              parse_mode="Markdown", reply_markup=get_main_menu())
        
    elif call.data == "buy":
        bot.send_message(call.message.chat.id, "📝 **Введите ваш PUBG ID и количество UC для заказа:**")
        # Здесь бот будет ждать ответа от пользователя

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
