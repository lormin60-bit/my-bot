import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8917035482:AAHu6Mvw8gccyBKDeeWadjMawcGgKVrlWxk"
OWNER_CHAT_ID = -5442797827

# ===== ДАННЫЕ СТУДИИ =====
SHOP_NAME = "Студия красоты Демо"
SERVICES = {
    "manicure": "💅 Маникюр — 1500 ₽",
    "pedicure": "🦶 Педикюр — 2000 ₽",
    "design": "🎨 Маникюр + дизайн — 2000 ₽",
    "extension": "💎 Наращивание ногтей — 2500 ₽",
    "brows": "🪮 Коррекция бровей — 800 ₽",
    "lashes": "👁 Наращивание ресниц — 1800 ₽",
}

MASTERS = {
    "anna": "👩 Анна",
    "maria": "👩 Мария",
    "olga": "👩 Ольга",
    "any": "🤷 Не важно",
}

DATES = ["15.09", "16.09", "17.09", "18.09", "19.09", "20.09", "21.09"]
TIMES = ["10:00", "11:30", "13:00", "14:30", "16:00", "17:30", "19:00"]

ADDRESS = "ул. Пример, 10"
PHONE = "+7 (999) 000-00-00"
WORK_HOURS = "10:00–21:00"

# ===== СОСТОЯНИЯ =====
class Booking(StatesGroup):
    service = State()
    master = State()
    date = State()
    time = State()
    name = State()
    phone = State()
    confirm = State()

# ===== КЛАВИАТУРЫ =====
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💅 Записаться", callback_data="book")],
        [InlineKeyboardButton(text="📋 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
    ])

def services_kb():
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"svc_{key}")] for key, name in SERVICES.items()]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def masters_kb():
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"mst_{key}")] for key, name in MASTERS.items()]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def dates_kb():
    buttons = [[InlineKeyboardButton(text=d, callback_data=f"date_{d}")] for d in DATES]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def times_kb():
    buttons = [[InlineKeyboardButton(text=t, callback_data=f"time_{t}")] for t in TIMES]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")],
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

# ===== СОЗДАНИЕ БОТА =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===== ХЭНДЛЕРЫ =====
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Добро пожаловать в студию красоты «{SHOP_NAME}»!\n\n"
        f"Здесь ты можешь записаться на маникюр, педикюр, "
        f"коррекцию бровей или наращивание ресниц за 30 секунд.\n\n"
        f"Что хочешь сделать?",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🏠 Главное меню:", reply_markup=main_menu())

@dp.callback_query(F.data == "services")
async def show_services(call: CallbackQuery):
    text = "📋 *Услуги и цены:*\n\n" + "\n".join(SERVICES.values())
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu())

@dp.callback_query(F.data == "contacts")
async def show_contacts(call: CallbackQuery):
    text = (
        f"📞 *Контакты:*\n\n"
        f"📍 Адрес: {ADDRESS}\n"
        f"📱 Телефон: {PHONE}\n"
        f"🕐 Работаем: {WORK_HOURS}"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=main_menu())

@dp.callback_query(F.data == "book")
async def book_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(Booking.service)
    await call.message.edit_text("💅 Выбери услугу:", reply_markup=services_kb())

@dp.callback_query(Booking.service, F.data.startswith("svc_"))
async def choose_service(call: CallbackQuery, state: FSMContext):
    key = call.data.replace("svc_", "")
    await state.update_data(service=SERVICES[key])
    await state.set_state(Booking.master)
    await call.message.edit_text("👩 Выбери мастера:", reply_markup=masters_kb())

@dp.callback_query(Booking.master, F.data.startswith("mst_"))
async def choose_master(call: CallbackQuery, state: FSMContext):
    key = call.data.replace("mst_", "")
    await state.update_data(master=MASTERS[key])
    await state.set_state(Booking.date)
    await call.message.edit_text("📅 Выбери дату:", reply_markup=dates_kb())

@dp.callback_query(Booking.date, F.data.startswith("date_"))
async def choose_date(call: CallbackQuery, state: FSMContext):
    date = call.data.replace("date_", "")
    await state.update_data(date=date)
    await state.set_state(Booking.time)
    await call.message.edit_text("🕐 Выбери время:", reply_markup=times_kb())

@dp.callback_query(Booking.time, F.data.startswith("time_"))
async def choose_time(call: CallbackQuery, state: FSMContext):
    time = call.data.replace("time_", "")
    await state.update_data(time=time)
    await state.set_state(Booking.name)
    await call.message.edit_text("👤 Как тебя зовут? Напиши имя:", reply_markup=back_kb())

@dp.message(Booking.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Booking.phone)
    await message.answer("📱 Оставь номер телефона для связи:", reply_markup=back_kb())

@dp.message(Booking.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    text = (
        "📋 *Проверь запись:*\n\n"
        f"💅 Услуга: {data['service']}\n"
        f"👩 Мастер: {data['master']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}"
    )
    await state.set_state(Booking.confirm)
    await message.answer(text, parse_mode="Markdown", reply_markup=confirm_kb())

@dp.callback_query(Booking.confirm, F.data == "confirm")
async def confirm(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = call.from_user

    await call.message.edit_text(
        f"✅ *Готово, {data['name']}!*\n\n"
        f"Ждём тебя {data['date']} в {data['time']}.\n"
        f"📍 Адрес: {ADDRESS}\n\n"
        f"За час до визита напомним. Если что-то изменится — напиши нам.",
        parse_mode="Markdown"
    )

    owner_text = (
        "🔔 *НОВАЯ ЗАПИСЬ!*\n\n"
        f"👤 Клиент: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"💬 Telegram: @{user.username or 'нет_ника'}\n\n"
        f"💅 Услуга: {data['service']}\n"
        f"👩 Мастер: {data['master']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}"
    )

    try:
        await bot.send_message(OWNER_CHAT_ID, owner_text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Не смог отправить уведомление: {e}")

    await state.clear()

@dp.callback_query(Booking.confirm, F.data == "cancel")
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Запись отменена. Возвращайся!", reply_markup=main_menu())

# ===== ЗАПУСК =====
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
