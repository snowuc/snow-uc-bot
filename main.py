import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7676835960
CARD_NUMBER = "5168 7500 0000 0000"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}


@app.route('/')
def home():
    return "Bot is live"


def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "🛒 Купить UC",
            callback_data="buy_menu"
        )
    )

    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в SNOW UC SHOP!\n\nВыберите действие:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id

    if call.data == "buy_menu":

        markup = types.InlineKeyboardMarkup(row_width=2)

        packs = [
            ("60 UC", "buy_60"),
            ("120 UC", "buy_120"),
            ("180 UC", "buy_180"),
            ("325 UC", "buy_325"),
            ("385 UC", "buy_385"),
            ("660 UC", "buy_660"),
            ("720 UC", "buy_720"),
            ("985 UC", "buy_985"),
            ("1045 UC", "buy_1045"),
            ("1320 UC", "buy_1320"),
            ("1440 UC", "buy_1440"),
            ("1800 UC", "buy_1800"),
            ("1920 UC", "buy_1920"),
            ("2125 UC", "buy_2125"),
            ("2460 UC", "buy_2460"),
            ("3120 UC", "buy_3120"),
            ("3850 UC", "buy_3850"),
            ("4510 UC", "buy_4510"),
            ("5650 UC", "buy_5650"),
            ("8100 UC", "buy_8100"),
            ("9900 UC", "buy_9900"),
            ("11950 UC", "buy_11950"),
            ("16200 UC", "buy_16200")
        ]

        buttons = [
            types.InlineKeyboardButton(text, callback_data=data)
            for text, data in packs
        ]

        markup.add(*buttons)

        bot.edit_message_text(
            "💎 Выберите пакет UC:",
            chat_id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data.startswith("buy_"):

        pack = call.data.replace("buy_", "")

        user_data[chat_id] = {
            "pack": pack
        }

        bot.edit_message_text(
            f"💎 Вы выбрали {pack} UC\n\nВведите ваш игровой ID (начинается на 5):",
            chat_id,
            call.message.message_id
        )

    elif call.data == "confirm_yes":

        bot.edit_message_text(
            f"💳 Оплатите заказ на карту:\n\n<code>{CARD_NUMBER}</code>\n\nПосле оплаты отправьте чек.",
            chat_id,
            call.message.message_id,
            parse_mode="HTML"
        )

    elif call.data == "confirm_no":

        if chat_id in user_data:
            del user_data[chat_id]

        bot.edit_message_text(
            "❌ Заказ отменён.\n\nНапишите /start для начала заново.",
            chat_id,
            call.message.message_id
        )


@bot.message_handler(
    func=lambda m: m.chat.id in user_data and "id" not in user_data[m.chat.id]
)
def handle_id(message):

    game_id = message.text.strip()

    if not game_id.startswith("5"):
        bot.reply_to(
            message,
            "❌ Игровой ID должен начинаться с цифры 5."
        )
        return

    user_data[message.chat.id]["id"] = game_id

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
        types.InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
    )

    try:
        with open("IMG_20260612_220910_235.jpg", "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=f"🎮 Ваш игровой ID:\n{game_id}\n\nВсё верно?",
                reply_markup=markup
            )

    except Exception as e:

        bot.send_message(
            message.chat.id,
            f"🎮 Ваш игровой ID:\n{game_id}\n\nВсё верно?",
            reply_markup=markup
        )

        print("Ошибка отправки фото:", e)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    if message.chat.id not in user_data:
        return

    data = user_data[message.chat.id]

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "Нет username"
    )

    caption = (
        f"🔔 НОВЫЙ ЗАКАЗ\n\n"
        f"👤 Имя: {user.first_name}\n"
        f"🆔 Telegram ID: {user.id}\n"
        f"📨 Username: {username}\n\n"
        f"🎮 Игровой ID: {data.get('id')}\n"
        f"💎 Пакет: {data.get('pack')} UC"
    )

    try:

        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=caption
        )

        bot.reply_to(
            message,
            "✅ Чек успешно отправлен администратору.\n\nОжидайте подтверждения."
        )

        del user_data[message.chat.id]

    except Exception as e:

        bot.reply_to(
            message,
            "❌ Ошибка отправки чека."
        )

        print("Ошибка:", e)


if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    print("Бот запущен...")
    bot.infinity_polling(skip_pending=True)
