import telebot
from telebot import types
import os
from flask import Flask, send_from_directory
from threading import Thread

# --- НАСТРОЙКИ ---
TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960
# Замени на свою ссылку после деплоя на Render
WEB_APP_URL = 'https://твое-имя.onrender.com/index.html'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_orders = {}

# --- ВЕБ-СЕРВЕР (для работы Mini App) ---
@app.route('/')
def home():
    return "Бот и Web App активны!"

@app.route('/index.html')
def serve_html():
    return send_from_directory('.', 'index.html')

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(url=WEB_APP_URL)
    markup.add(types.InlineKeyboardButton("🛒 Открыть магазин", web_app=web_app))
    
    welcome_text = (
        "<b>✨ Добро пожаловать в SNOW UC SHOP!</b>\n\n"
        "Нажми кнопку ниже, чтобы выбрать пак через наш магазин."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

# Прием данных из Mini App
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    data = message.web_app_data.data
    chat_id = message.chat.id
    user_orders[chat_id] = {'amount': data}
    
    bot.send_message(chat_id, f"✅ Вы выбрали: <b>{data}</b>.\nТеперь введите ваш <b>PUBG ID:</b>", parse_mode="HTML")
    bot.register_next_step_handler(message, get_pubg_id)

def get_pubg_id(message):
    chat_id = message.chat.id
    user_orders[chat_id]['pubg_id'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 Монобанк", callback_data="pay_monobank"),
        types.InlineKeyboardButton("🏦 ПриватБанк", callback_data="pay_privatbank")
    )
    bot.send_message(chat_id, "✅ ID получен! Выберите способ оплаты:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def process_payment(call):
    chat_id = call.message.chat.id
    bank = call.data.split("_")[1]
    order = user_orders.get(chat_id)
    
    card = "5168 7500 0000 0000" # Твой номер карты
    
    text = (f"💳 <b>Оформление оплаты</b>\n\n"
            f"Пак: <b>{order['amount']}</b>\n"
            f"ID: <code>{order.get('pubg_id')}</code>\n"
            f"Банк: <b>{bank.capitalize()}</b>\n\n"
            f"💳 Карта: <code>{card}</code>\n\n"
            f"<i>После оплаты отправьте чек в этот чат!</i>")
    
    bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "✅ Чек принят! Ожидайте зачисления.")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
("🛒 Купить UC", callback_data="buy_menu"))
    welcome_text = (
        "<b>✨ Добро пожаловать в SNOW UC SHOP!</b>\n\n"
        "Лучший сервис по пополнению PUBG Mobile.\n"
        "<i>Нажми кнопку ниже, чтобы начать:</i>"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 60 UC", callback_data="pack_60"),
            types.InlineKeyboardButton("💎 325 UC", callback_data="pack_325"),
            types.InlineKeyboardButton("💎 660 UC", callback_data="pack_660")
        )
        bot.edit_message_text("📦 <b>Выберите желаемый пак UC:</b>", chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

    elif call.data.startswith("pack_"):
        amount = call.data.split("_")[1]
        user_orders[chat_id] = {'amount': amount}
        bot.edit_message_text("📝 <b>Введите ваш PUBG ID:</b>\n\n<i>Отправьте его следующим сообщением:</i>", chat_id, call.message.message_id, parse_mode="HTML")
        bot.register_next_step_handler(call.message, get_pubg_id)

    elif call.data.startswith("pay_"):
        bank = call.data.split("_")[1]
        order = user_orders.get(chat_id)
        
        card = "5168 7500 0000 0000" # Замени на свою карту
        
        text = (f"💳 <b>Оформление оплаты</b>\n\n"
                f"Пак: <b>{order['amount']} UC</b>\n"
                f"ID: <code>{order.get('pubg_id', 'не указан')}</code>\n"
                f"Банк: <b>{bank.capitalize()}</b>\n\n"
                f"💰 К оплате: <b>[Твоя сумма] грн</b>\n"
                f"💳 Карта: <code>{card}</code>\n\n"
                f"<i>После оплаты отправьте чек (скриншот) в этот чат!</i>")
        
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML")

def get_pubg_id(message):
    chat_id = message.chat.id
    if not user_orders.get(chat_id):
        user_orders[chat_id] = {}
    user_orders[chat_id]['pubg_id'] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💳 Монобанк", callback_data="pay_monobank"),
        types.InlineKeyboardButton("🏦 ПриватБанк", callback_data="pay_privatbank")
    )
    bot.send_message(chat_id, "✅ <b>ID получен!</b>\nВыберите способ оплаты:", reply_markup=markup, parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "✅ <b>Чек принят!</b>\nОжидайте зачисления UC.")
    bot.send_message(ADMIN_ID, f"📸 <b>Новый заказ!</b>\nПользователь: @{message.from_user.username}\nID: {user_orders.get(message.chat.id, {}).get('pubg_id')}", parse_mode="HTML")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

if __name__ == "__main__":
    Thread(target=run_server).start()
    bot.infinity_polling()
