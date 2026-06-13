import telebot
from telebot import types
import os
import sqlite3
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7676835960"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# СЛОВАРЬ ЦЕН: Вы можете изменить любую цену прямо здесь
PACKS = {
    "60": "150 ₽", "120": "300 ₽", "180": "450 ₽", "325": "750 ₽", 
    "385": "900 ₽", "660": "1500 ₽", "720": "1650 ₽", "985": "2200 ₽", 
    "1045": "2350 ₽", "1320": "2900 ₽", "1440": "3150 ₽", "1800": "3900 ₽", 
    "1920": "4150 ₽", "2125": "4500 ₽", "2460": "5200 ₽", "3120": "6500 ₽", 
    "3850": "7900 ₽", "4510": "9200 ₽", "5650": "11500 ₽", "8100": "15900 ₽", 
    "9900": "19500 ₽", "11950": "23500 ₽", "16200": "31900 ₽"
}

waiting_for_id = {}

# Инициализация базы данных для сохранения ID
def init_db():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            game_id TEXT
        )
    """)
    conn.commit()
    conn.close()

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
    
    # 1. Меню выбора паков (теперь с ценами)
    if call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for uc, price in PACKS.items():
            buttons.append(types.InlineKeyboardButton(f"{uc} UC — {price}", callback_data=f"pack_{uc}"))
        markup.add(*buttons)
        bot.edit_message_text("💎 Выберите пак и цену:", chat_id, call.message.message_id, reply_markup=markup)
    
    # 2. Клик по паку -> Проверка сохраненного ID
    elif call.data.startswith("pack_"):
        pack_value = call.data.split("_")[1]
        price_value = PACKS.get(pack_value, "0")
        waiting_for_id[chat_id] = {"pack": pack_value, "price": price_value}
        
        # Проверяем в базе данных, покупал ли этот человек раньше
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT game_id FROM users WHERE chat_id = ?", (str(chat_id),))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            saved_id = row[0]
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(f"✅ Да, использовать ID: {saved_id}", callback_data="use_saved_id"))
            markup.row(types.InlineKeyboardButton("✏️ Ввести другой ID", callback_data="enter_new_id"))
            bot.edit_message_text(f"🛍 Выбрано: {pack_value} UC за {price_value}.\n\nУ вас есть сохраненный ID: <code>{saved_id}</code>. Использовать его?", 
                                   chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.edit_message_text(f"✅ Выбрано: {pack_value} UC за {price_value}.\n\nВведите ваш игровой ID (начинается на 5):", chat_id, call.message.message_id)

    # 2.1 Клиент выбрал использовать старый ID
    elif call.data == "use_saved_id":
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT game_id FROM users WHERE chat_id = ?", (str(chat_id),))
        saved_id = cursor.fetchone()[0]
        conn.close()
        
        waiting_for_id[chat_id]["id"] = saved_id
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        bot.delete_message(chat_id, call.message.message_id)
        
        try:
            bot.send_photo(chat_id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                           caption=f"Ваш ID: {saved_id}. Верно?", reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, f"ID: {saved_id}. Нажмите кнопку для оплаты:", reply_markup=markup)

    # 2.2 Клиент хочет ввести новый ID вместо старого
    elif call.data == "enter_new_id":
        if chat_id in waiting_for_id and "id" in waiting_for_id[chat_id]:
            del waiting_for_id[chat_id]["id"]
        bot.edit_message_text("Введите новый игровой ID (начинается на 5):", chat_id, call.message.message_id)

    # 3. Подтверждение перехода к оплате
    elif call.data == "confirm":
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "💳 Карта: <code>5168 7500 0000 0000</code>.\n\n📸 Пришлите скриншот чека.", parse_mode="HTML")

    # --- АДМИН: ВЫПОЛНЕНО ---
    elif call.data.startswith("done_"):
        if str(chat_id) == ADMIN_ID: 
            client_id = call.data.split("_")[1]
            try:
                bot.send_message(client_id, "✅ Ваш заказ успешно выполнен! UC начислены на ваш аккаунт. Спасибо за покупку!")
                bot.edit_message_caption(caption=call.message.caption + "\n\n✅ СТАТУС: ВЫПОЛНЕНО", chat_id=chat_id, message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка отправки пользователю.")

    # --- АДМИН: ОТКЛОНЕНО ---
    elif call.data.startswith("reject_"):
        if str(chat_id) == ADMIN_ID:
            client_id = call.data.split("_")[1]
            try:
                bot.send_message(client_id, "❌ Ваш заказ отклонен.\n\nПричина: Неверная сумма или недействительный чек.\nПожалуйста, проверьте данные и оформите заказ заново.")
                bot.edit_message_caption(caption=call.message.caption + "\n\n❌ СТАТУС: ОТКЛОНЕН (Неверная сумма)", chat_id=chat_id, message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка отправки пользователю.")

@bot.message_handler(func=lambda m: m.chat.id in waiting_for_id and "id" not in waiting_for_id[m.chat.id])
def handle_id(message):
    if message.text.startswith('5'):
        game_id = message.text
        waiting_for_id[message.chat.id]["id"] = game_id
        
        # Сохраняем или обновляем ID пользователя в базе данных
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (chat_id, game_id) VALUES (?, ?)", (str(message.chat.id), str(game_id)))
        conn.commit()
        conn.close()
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        
        try:
            bot.send_photo(message.chat.id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                           caption=f"Ваш ID: {game_id}. Верно?", reply_markup=markup)
        except Exception:
            bot.send_message(message.chat.id, f"ID: {game_id}. Нажмите кнопку для оплаты:", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться с 5.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id in waiting_for_id and "id" in waiting_for_id[message.chat.id]:
        data = waiting_for_id[message.chat.id]
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.row(types.InlineKeyboardButton("✅ Заказ выполнен", callback_data=f"done_{message.chat.id}"))
        admin_markup.row(types.InlineKeyboardButton("❌ Отклонить (Неверная сумма)", callback_data=f"reject_{message.chat.id}"))
        
        # Передаем админу Пак, Сумму и ID
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                       caption=f"🔔 НОВЫЙ ЗАКАЗ!\nКлиент: @{message.from_user.username or message.chat.id}\nID: {data['id']}\nПак: {data['pack']} UC\nСумма к получению: {data['price']}",
                       reply_markup=admin_markup)
        bot.reply_to(message, "✅ Чек получен! Ожидайте зачисления.")
        del waiting_for_id[message.chat.id]

if __name__ == '__main__':
    init_db() # Создаем базу данных при запуске
    Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
