import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = '8769000983:AAGW8ulr7xGM4Sd_M7KoqGJlrU3RzgLfo4E'
ADMIN_ID = 7676835960

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Словарь для хранения данных заказа клиента
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💰 Купить UC", callback_data="buy"))
    bot.send_message(message.chat.id, "❄️ SNOW UC SHOP - добро пожаловать!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    # 1. Выбор пака
    if call.data == "buy":
        markup = types.InlineKeyboardMarkup(row_width=2)
        packs = [("60 UC", "60"), ("325 UC", "325"), ("660 UC", "660")]
        for name, amount in packs:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"pack_{amount}"))
        bot.edit_message_text("Выберите пак:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. Запрос PUBG ID
    elif call.data.startswith("pack_"):
        amount = call.data.split("_")[1]
        user_data[call.message.chat.id] = {'amount': amount}
        bot.edit_message_text("Введите ваш PUBG ID:", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, get_id)

    # 3. Выбор банка
    elif call.data.startswith("pay_"):
        bank = call.data.split("_")[1]
        data = user_data.get(call.message.chat.id)
        text = f"✅ Заказ оформлен!\nПак: {data['amount']} UC\nID: {data['pubg_id']}\nБанк: {bank}\n\nРеквизиты: [номер карты]\n\nОплатите и пришлите чек!"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)

def get_id(message):
    user_data[message.chat.id]['pubg_id'] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💳 Монобанк", callback_data="pay_Monobank"))
    markup.add(types.InlineKeyboardButton("🏦 ПриватБанк", callback_data="pay_Privatbank"))
    bot.send_message(message.chat.id, "Выберите метод оплаты:", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))).start()
    bot.infinity_polling()
