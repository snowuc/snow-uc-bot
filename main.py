import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище заказов
user_orders = {}

# Веб-сервер, чтобы Render не «засыпал»
@app.route('/')
def home():
    return "Бот работает стабильно!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА БОТА ---

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    
    welcome_text = (
        "<b>✨ Добро пожаловать в SNOW UC SHOP!</b>\n\n"
        "Лучший сервис по пополнению PUBG Mobile.\n"
        "<i>Нажми кнопку ниже, чтобы начать:</i>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    # Меню выбора паков
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 60 UC", callback_data="pack_60 UC"),
            types.InlineKeyboardButton("💎 325 UC", callback_data="pack_325 UC"),
            types.InlineKeyboardButton("💎 660 UC", callback_data="pack_660 UC")
        )
        bot.edit_message_text("📦 <b>Выберите желаемый пак UC:</b>", chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

    # После выбора пака — запрашиваем PUBG ID
    elif call.data.startswith("pack_"):
        amount = call.data.split("_")[1]
        user_orders[chat_id] = {'amount': amount}
        
        bot.edit_message_text("📝 <b>Введите ваш PUBG ID:</b>\n\n<i>Отправьте его следующим сообщением в чат:</i>", chat_id, call.message.message_id, parse_mode="HTML")
        bot.register_next_step_handler(call.message, get_pubg_id)

    # Выбор банка для оплаты
    elif call.data.startswith("pay_"):
        bank = call.data.split("_")[1]
        order = user_orders.get(chat_id, {"amount": "Не выбран", "pubg_id": "Не указан"})
        
        card = "5168 7500 0000 0000" # Замени на свою карту
        
        text = (f"💳 <b>Оформление оплаты</b>\n\n"
                f"Пак: <b>{order['amount']}</b>\n"
                f"ID игрока: <code>{order.get('pubg_id')}</code>\n"
                f"Банк: <b>{bank.capitalize()}</b>\n\n"
                f"💳 Карта для перевода: <code>{card}</code>\n\n
