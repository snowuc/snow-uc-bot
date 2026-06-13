import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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
    bot.answer_callback_query(call.id)
    
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Вернул все 23 пака для финальной версии
        packs = [("60 UC", "60"), ("120 UC", "120"), ("180 UC", "180"), ("325 UC", "325"), 
                 ("385 UC", "385"), ("660 UC", "660"), ("720 UC", "720"), ("985 UC", "985"), 
                 ("1045 UC", "1045"), ("1320 UC", "1320"), ("1440 UC", "1440"), ("1800 UC", "1800"), 
                 ("1920 UC", "1920"), ("2125 UC", "2125"), ("2460 UC", "2460"), ("3120 UC", "3120"), 
                 ("3850 UC", "3850"), ("4510 UC", "4510"), ("5650 UC", "5650"), ("8100 UC", "8100"), 
                 ("9900 UC", "9900"), ("11950 UC", "11950"), ("16200 UC", "16200")]
        markup.add(*[types.InlineKeyboardButton(p[0], callback_data=f"pack_{p[1]}") for p in packs])
        bot.edit_message_text("💎 Выберите пак:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("pack_"):
        pack_value = call.data.split("_")[1]
        waiting_for_id[chat_id] = {"pack": pack_value}
        bot.edit_message_text(f"✅ Выбрано: {pack_value} UC. Введите ID (начинается на 5):", chat_id, call.message.message_id)

    elif call.data == "confirm":
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "💳 Карта: <code>5168 7500 0000 0000</code>.\n\n📸 Пришлите скриншот чека.", parse_mode="HTML")

    # --- ЛОГИКА ДЛЯ АДМИНА (ВЫПОЛНЕНО) ---
    elif call.data.startswith("done_"):
        if str(chat_id) == ADMIN_ID: 
            client_id = call.data.split("_")[1]
            try:
                bot.send_message(client_id, "✅ Ваш заказ успешно выполнен! UC начислены на ваш аккаунт. Спасибо за покупку!")
                bot.edit_message_caption(caption=call.message.caption + "\n\n✅ СТАТУС: ВЫПОЛНЕНО", 
                                         chat_id=chat_id, 
                                         message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка отправки пользователю.")

    # --- ЛОГИКА ДЛЯ АДМИНА (ОТКЛОНЕНО) ---
    elif call.data.startswith("reject_"):
        if str(chat_id) == ADMIN_ID:
            client_id = call.data.split("_")[1]
            try:
                bot.send_message(client_id, "❌ Ваш заказ отклонен.\n\nПричина: Неверная сумма или недействительный чек.\nПожалуйста, проверьте данные и оформите заказ заново.")
                bot.edit_message_caption(caption=call.message.caption + "\n\n❌ СТАТУС: ОТКЛОНЕН (Неверная сумма)", 
                                         chat_id=chat_id, 
                                         message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка отправки пользователю.")

@bot.message_handler(func=lambda m: m.chat.id in waiting_for_id and "id" not in waiting_for_id[m.chat.id])
def handle_id(message):
    if message.text.startswith('5'):
        waiting_for_id[message.chat.id]["id"] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        
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
        
        # --- 2 КНОПКИ ДЛЯ АДМИНА ---
        admin_markup = types.InlineKeyboardMarkup()
        # Размещаем кнопки друг под другом для удобства
        admin_markup.row(types.InlineKeyboardButton("✅ Заказ выполнен", callback_data=f"done_{message.chat.id}"))
        admin_markup.row(types.InlineKeyboardButton("❌ Отклонить (Неверная сумма)", callback_data=f"reject_{message.chat.id}"))
        
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                       caption=f"🔔 НОВЫЙ ЗАКАЗ!\nКлиент: @{message.from_user.username or message.chat.id}\nID: {data['id']}\nПак: {data['pack']} UC",
                       reply_markup=admin_markup)
        bot.reply_to(message, "✅ Чек получен! Ожидайте зачисления.")
        del waiting_for_id[message.chat.id]

if __name__ == '__main__':
    Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
