import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# === Читаем токен ===
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# === Слова ===
WORDS = [
    "Арбуз", "Тачка", "Переулок", "Гараж", "Кабан", "Шоколад", "Кроссовки",
    "Огнемёт", "Трактор", "Кефир", "Бассейн", "Фонарик", "Сковородка", "Кофемашина",
    "Панда", "Грузовик", "Троллейбус", "Ковёр", "Лимонад", "Каска", "Пицца",
    "Ракета", "Кирпич", "Окно", "Стекло", "Кот", "Пельмени", "Провод", "Розетка",
    "Карта", "Телефон", "Карандаш", "Герой", "Танк", "Шахта", "Охранник",
    "Пушка", "Рюкзак", "Кровать", "Лопата", "Бита", "Шляпа", "Велосипед",
    "Консоль", "Древесина", "Якорь", "Горка", "Бургер", "Прикол"
]

# === состояние игры ===
game = {
    "word": None,
    "players": [],
    "spy": None,
    "current": 0,
    "chat_id": None,
    "prompt_msg_id": None
}

# === кнопки ===
def view_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="👁 Посмотреть", callback_data="view")
    return kb.as_markup()

def next_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="➡ Следующий игрок", callback_data="next")
    return kb.as_markup()

# === /start ===
@dp.message(F.text == "/start")
async def start_cmd(msg: Message):
    game["players"] = []
    game["current"] = 0
    game["chat_id"] = msg.chat.id

    sent = await msg.answer(
        "🎮 <b>Игра Шпион</b>\n\n"
        "Введите имена игроков через пробел."
    )

    game["prompt_msg_id"] = sent.message_id

# === получаем игроков ===
@dp.message()
async def get_players(msg: Message):
    if game["chat_id"] is None:
        await msg.answer("Напиши /start")
        return

    players = [p.strip() for p in msg.text.split(" ") if p.strip()]
    if len(players) < 3:
        await msg.answer("Минимум 3 игрока.")
        return

    game["players"] = players
    game["current"] = 0

    game["word"] = random.choice(WORDS)
    game["spy"] = random.randint(0, len(players) - 1)

    # Чистим чат
    try:
        await msg.delete()
        await bot.delete_message(game["chat_id"], game["prompt_msg_id"])
    except:
        pass

    await msg.answer(
        f"Передайте телефон игроку: <b>{players[0]}</b>",
        reply_markup=view_button()
    )

# === посмотреть ===
@dp.callback_query(F.data == "view")
async def view_role(clb: CallbackQuery):
    idx = game["current"]
    name = game["players"][idx]

    if idx == game["spy"]:
        text = f"🕵 <b>{name}</b> — ШПИОН!"
    else:
        text = f"🔤 <b>{name}</b>, твоё слово: <b>{game['word']}</b>"

    await clb.message.answer(text, reply_markup=next_button())

    try:
        await clb.message.delete()
    except:
        pass

    await clb.answer()

# === следующий ===
@dp.callback_query(F.data == "next")
async def next_player(clb: CallbackQuery):
    try:
        await clb.message.delete()
    except:
        pass

    game["current"] += 1

    # все посмотрели
    if game["current"] >= len(game["players"]):
        # отправляем видео
        video = FSInputFile("timer.mp4")
        timer_msg = await clb.message.answer_video(video)

        # ждём 3 минуты
        await asyncio.sleep(180)

        # удаляем видео
        try:
            await bot.delete_message(game["chat_id"], timer_msg.message_id)
        except:
            pass

        await clb.message.answer("⏰ Время вышло! Голосуйте.")
        return

    next_name = game["players"][game["current"]]
    await clb.message.answer(
        f"Передайте телефон игроку: <b>{next_name}</b>",
        reply_markup=view_button()
    )

    await clb.answer()

# === запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
