import asyncio
import logging
import hashlib
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

# Включаем логирование, чтобы видеть ошибки в консоли
logging.basicConfig(level=logging.INFO)

# ТВОЙ ТОКЕН УЖЕ ЗДЕСЬ 🔐
BOT_TOKEN = "8986699759:AAHc-RqjhrDM9kDoQmE2qT5ONnOWZ_fSSLk"

# Настройки твоего поставщика UC (API реселлера Midasbuy)
PROVIDER_API_URL = "https://api.vash-postavshik.com/v1/topup"
PROVIDER_KEY = "ВАШ_КЛЮЧ_ПОСТАВЩИКА_UC"

# Константы для нашего товара
UC_AMOUNT = 60
PRICE_UAH = 45

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для Машины Состояний (FSM)
class BuyProcess(StatesGroup):
    waiting_for_id = State()

# 1. Стартовая кнопка или команда
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🛒 Купить {UC_AMOUNT} UC — {PRICE_UAH} грн", callback_data="buy_60_uc")
    await message.answer("Добро пожаловать в шоп! Нажмите кнопку ниже для покупки:", reply_markup=builder.as_markup())

# 2. Обработка клика по кнопке -> запрашиваем ID
@dp.callback_query(F.data == "buy_60_uc")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите ваш игровой **Player ID (UID)** из PUBG Mobile:")
    await state.set_state(BuyProcess.waiting_for_id)
    await callback.answer()

# 3. Получаем ID, проверяем его и генерируем ссылку на оплату
@dp.message(BuyProcess.waiting_for_id)
async def process_uid_and_create_invoice(message: types.Message, state: FSMContext):
    player_id = message.text.strip()
    
    # Простая проверка, что ID состоит только из цифр
    if not player_id.isdigit() or len(player_id) < 5:
        return await message.answer("❌ Ошибка! Введите корректный цифровой ID.")
    
    # Сохраняем ID игрока во временную память бота
    await state.update_data(player_id=player_id)
    
    # Уникальный номер заказа (используем ID пользователя Telegram и время)
    order_id = f"{message.from_user.id}_{int(asyncio.get_event_loop().time())}"
    
    # --- ГЕНЕРАЦИЯ ССЫЛКИ НА ОПЛАТУ (Пример для Payok) ---
    merchant_id = "12345"  # Ваш ID в платежной системе
    secret_word = "secret_key_from_payment" # Ваш секретный ключ из платежки
    
    # Создаем подпись (Sign) для безопасности платежа
    sign_str = f"{PRICE_UAH}:{order_id}:{merchant_id}:UAH:{secret_word}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    # Конструируем ссылку, куда перенаправим клиента
    payment_url = f"https://payok.io/pay?desc=PUBG_{UC_AMOUNT}UC&currency=UAH&shop={merchant_id}&payment={order_id}&amount={PRICE_UAH}&sign={sign}"
    
    # Кнопка для перехода к оплате
    pay_builder = InlineKeyboardBuilder()
    pay_builder.button(text="💳 Оплатить 45 грн", url=payment_url)
    
    await message.answer(
        f"✅ Заказ сформирован!\n\n"
        f"**Товар:** {UC_AMOUNT} UC\n"
        f"**Игровой ID:** `{player_id}`\n"
        f"**Сумма к оплате:** {PRICE_UAH} UAH\n\n"
        f"Нажмите кнопку ниже, чтобы перейти на сайт оплаты. После успешного платежа UC начислятся автоматически.",
        parse_mode="Markdown",
        reply_markup=pay_builder.as_markup()
    )
    
    await state.update_data(order_id=order_id)

# --- 4. ФУНКЦИЯ НАЧИСЛЕНИЯ UC (Вызывается сервером после получения Вебхука от платежки) ---
async def auto_delivery_uc(player_id: str, amount: int):
    headers = {"Authorization": f"Bearer {PROVIDER_KEY}"}
    payload = {
        "game": "pubg_mobile",
        "player_id": player_id,
        "amount": amount
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(PROVIDER_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    logging.info(f"Успешное авто-пополнение {amount} UC для ID {player_id}")
                    return True
                else:
                    logging.error(f"Ошибка поставщика! Статус: {response.status}")
                    return False
        except Exception as e:
            logging.error(f"Не удалось связаться с API поставщика: {e}")
            return False

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
