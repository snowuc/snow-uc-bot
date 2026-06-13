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

PACKS = {
    "60": "41 ₴", "120": "82 ₴", "180": "123 ₴", "325": "215 ₴", 
    "385": "250 ₴", "660": "400 ₴", "720": "440 ₴", "985": "615 ₴", 
    "1045": "655 ₴", "1320": "790 ₴", "1440": "870 ₴", "1800": "1.020 ₴", 
    "1920": "1.100 ₴", "2125": "1.205 ₴", "2460": "1.390 ₴", "3120": "1.785 ₴", 
    "3850": "2.000 ₴", "4510": "2.380 ₴", "5650": "3.030 ₴", "8100": "3.900 ₴", 
    "9900": "4.920 ₴", "11950": "5.900 ₴", "16200": "7.800 ₴"
}

# Словари состояний
waiting_for_id = {}          # Для процесса покупки
changing_profile_id = {}     # Для смены ID в профиле

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

# Красивое главное меню с новыми кнопками
def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛒 Купить UC", callback_data="buy_menu"))
    markup.add(
        types.InlineKeyboardButton("👤 Мой профиль", callback_data="profile"),
        types.InlineKeyboardButton("ℹ️ FAQ", callback_data="faq")
    )
    markup.add(types.InlineKeyboardButton("👨‍💻 Поддержка", callback_data="support"))
    return markup

@app.route('/')
def home(): return "Bot is live"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привет! Добро пожаловать в SNOW UC SHOP!", reply_markup=main_menu_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    # --- НАВИГАЦИЯ ---
    if call.data == "to_main_menu":
        if chat_id in changing_profile_id: del changing_profile_id[chat_id]
        bot.edit_message_text("👋 Добро пожаловать в SNOW UC SHOP!", chat_id, call.message.message_id, reply_markup=main_menu_markup())

    # --- ИНФОРМАЦИЯ И ПОДДЕРЖКА ---
    elif call.data == "faq":
        text = ("ℹ️ <b>Информация и FAQ</b>\n\n"
                "⏱ <b>Время доставки:</b> от 5 до 15 минут после отправки чека.\n"
                "🛡 <b>Гарантии:</b> Мы работаем честно и дорожим репутацией. UC пополняются строго по официальным каналам.\n"
                "🕒 <b>График работы:</b> Ежедневно без выходных.")
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu"))
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "support":
        # ВАЖНО: Замени @твой_ник_тут на свой реальный юзернейм!
        text = ("👨‍💻 <b>Поддержка</b>\n\n"
                "Если у вас возникли вопросы, задерживается оплата или нужен индивидуальный заказ, пишите администратору:\n\n"
                "👉 <b>@твой_ник_тут</b>")
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu"))
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    # --- ПРОФИЛЬ ---
    elif call.data == "profile":
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT game_id FROM users WHERE chat_id = ?", (str(chat_id),))
        row = cursor.fetchone()
        conn.close()
        
        saved_id = row[0] if row else "❌ Не указан"
        
        text = f"👤 <b>Ваш профиль</b>\n\n🆔 Игровой ID: <code>{saved_id}</code>\n\n<i>Здесь будет отображаться статистика ваших покупок.</i>"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✏️ Изменить ID", callback_data="profile_change_id"))
        markup.add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu"))
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "profile_change_id":
        changing_profile_id[chat_id] = True
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Отмена", callback_data="profile"))
        bot.edit_message_text("✏️ Введите ваш новый игровой ID (начинается на 5):", chat_id, call.message.message_id, reply_markup=markup)

    # --- ПОКУПКА ---
    elif call.data == "buy_menu":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(f"{uc} UC — {price}", callback_data=f"pack_{uc}") for uc, price in PACKS.items()]
        markup.add(*buttons)
        markup.row(types.InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu"))
        bot.edit_message_text("💎 Выберите пак и цену:", chat_id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("pack_"):
        pack_value = call.data.split("_")[1]
        price_value = PACKS.get(pack_value, "0")
        waiting_for_id[chat_id] = {"pack": pack_value, "price": price_value}
        
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT game_id FROM users WHERE chat_id = ?", (str(chat_id),))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            saved_id = row[0]
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton(f"✅ Использовать ID: {saved_id}", callback_data="use_saved_id"))
            markup.row(types.InlineKeyboardButton("✏️ Ввести другой ID", callback_data="enter_new_id"))
            markup.row(types.InlineKeyboardButton("🔙 Отмена", callback_data="buy_menu"))
            bot.edit_message_text(f"🛍 Выбрано: {pack_value} UC за {price_value}.\n\nСохраненный ID: <code>{saved_id}</code>. Использовать его?", 
                                   chat_id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
        else:
            back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад к пакам", callback_data="buy_menu"))
            bot.edit_message_text(f"✅ Выбрано: {pack_value} UC за {price_value}.\n\nВведите ваш игровой ID (начинается на 5):", 
                                   chat_id, call.message.message_id, reply_markup=back_markup)

    elif call.data == "use_saved_id":
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("SELECT game_id FROM users WHERE chat_id = ?", (str(chat_id),))
        saved_id = cursor.fetchone()[0]
        conn.close()
        
        waiting_for_id[chat_id]["id"] = saved_id
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        markup.row(types.InlineKeyboardButton("🔙 Назад", callback_data="buy_menu"))
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_photo(chat_id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                       caption=f"Ваш ID: {saved_id}. Верно?", reply_markup=markup)

    elif call.data == "enter_new_id":
        if chat_id in waiting_for_id and "id" in waiting_for_id[chat_id]: del waiting_for_id[chat_id]["id"]
        back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад к пакам", callback_data="buy_menu"))
        bot.edit_message_text("Введите новый игровой ID (начинается на 5):", chat_id, call.message.message_id, reply_markup=back_markup)

    elif call.data == "confirm":
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "💳 Карта: <code>5168 7500 0000 0000</code>.\n\n📸 Пришлите <b>ФОТОГРАФИЮ (скриншот)</b> чека.", parse_mode="HTML")

    # --- АДМИН ПАНЕЛЬ ---
    elif call.data.startswith("done_"):
        if str(chat_id) == ADMIN_ID: 
            client_id = call.data.split("_")[1]
            try:
                client_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🛒 Купить еще UC", callback_data="buy_menu"))
                bot.send_message(client_id, "✅ Ваш заказ успешно выполнен! UC начислены. Спасибо за покупку!", reply_markup=client_markup)
                bot.edit_message_caption(caption=call.message.caption + "\n\n✅ СТАТУС: ВЫПОЛНЕНО", chat_id=chat_id, message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка: пользователь заблокировал бота.")

    elif call.data.startswith("reject_"):
        if str(chat_id) == ADMIN_ID:
            client_id = call.data.split("_")[1]
            try:
                client_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔄 Оформить заново", callback_data="buy_menu"))
                bot.send_message(client_id, "❌ Ваш заказ отклонен.\nПричина: Неверная сумма или недействительный чек.", reply_markup=client_markup)
                bot.edit_message_caption(caption=call.message.caption + "\n\n❌ СТАТУС: ОТКЛОНЕН", chat_id=chat_id, message_id=call.message.message_id)
            except Exception:
                bot.send_message(ADMIN_ID, "❌ Ошибка: пользователь заблокировал бота.")

# Обработка смены ID в профиле
@bot.message_handler(func=lambda m: m.chat.id in changing_profile_id)
def handle_profile_id_change(message):
    if message.text.startswith('5'):
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (chat_id, game_id) VALUES (?, ?)", (str(message.chat.id), str(message.text)))
        conn.commit()
        conn.close()
        del changing_profile_id[message.chat.id]
        bot.reply_to(message, f"✅ Ваш ID успешно сохранен: {message.text}", reply_markup=main_menu_markup())
    else:
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться с 5.")

# Обработка ввода ID при покупке
@bot.message_handler(func=lambda m: m.chat.id in waiting_for_id and "id" not in waiting_for_id[m.chat.id])
def handle_id(message):
    if message.text.startswith('5'):
        game_id = message.text
        waiting_for_id[message.chat.id]["id"] = game_id
        
        conn = sqlite3.connect("shop.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (chat_id, game_id) VALUES (?, ?)", (str(message.chat.id), str(game_id)))
        conn.commit()
        conn.close()
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm"))
        markup.row(types.InlineKeyboardButton("🔙 Изменить пак", callback_data="buy_menu"))
        bot.send_photo(message.chat.id, "https://raw.githubusercontent.com/snowuc/snow-uc-bot/main/IMG_20260612_220910_235.jpg", 
                       caption=f"Ваш ID: {game_id}. Верно?", reply_markup=markup)
    else:
        back_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад к пакам", callback_data="buy_menu"))
        bot.reply_to(message, "❌ Ошибка: ID должен начинаться с 5.", reply_markup=back_markup)

# Защита от дурака: если клиент шлет текст/файл вместо чека
@bot.message_handler(content_types=['text', 'document', 'video', 'sticker', 'audio', 'voice', 'animation'], 
                     func=lambda m: m.chat.id in waiting_for_id and "id" in waiting_for_id[m.chat.id])
def handle_wrong_receipt(message):
    bot.reply_to(message, "❌ Пожалуйста, отправьте именно **ФОТОГРАФИЮ** (скриншот) чека. Бот не принимает текст или файлы.", parse_mode="Markdown")

# Правильная обработка фото-чека
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id in waiting_for_id and "id" in waiting_for_id[message.chat.id]:
        data = waiting_for_id[message.chat.id]
        
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.row(types.InlineKeyboardButton("✅ Заказ выполнен", callback_data=f"done_{message.chat.id}"))
        admin_markup.row(types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{message.chat.id}"))
        
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                       caption=f"🔔 НОВЫЙ ЗАКАЗ!\nКлиент: @{message.from_user.username or message.chat.id}\nID: {data['id']}\nПак: {data['pack']} UC\nСумма: {data['price']}",
                       reply_markup=admin_markup)
        
        client_menu_markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 В главное меню", callback_data="to_main_menu"))
        bot.reply_to(message, "✅ Чек получен! Ожидайте зачисления.", reply_markup=client_menu_markup)
        del waiting_for_id[message.chat.id]

if __name__ == '__main__':
    init_db() 
    Thread(target=run_server, daemon=True).start()
    bot.infinity_polling()
