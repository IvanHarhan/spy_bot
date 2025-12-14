import asyncio
import random
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ===== TOKEN =====
TOKEN = Path("token.txt").read_text().strip()

bot = Bot(
    TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ===== GAME STATE =====
players = []
roles = {}
current_index = 0
word = ""
video_message_id = None

WORDS = [
    "Аэропорт", "Библиотека", "Школа", "Университет", "Метро", "Больница",
    "Стадион", "Ресторан", "Кинотеатр", "Отель", "Казино", "Пляж",
    "Парк", "Зоопарк", "Аквапарк", "Ферма", "Рынок", "Супермаркет",
    "Полицейский участок", "Тюрьма", "Пожарная часть", "Церковь",
    "Мечеть", "Музей", "Театр", "Цирк", "Кафе", "Бар",
    "Ночной клуб", "Клуб", "Бассейн", "Спортзал", "Сауна",
    "Гараж", "Автосервис", "Заправка", "Магазин одежды",
    "Бутик", "Ломбард", "Банк", "Обменник", "Офис",
    "Колл-центр", "Склад", "Порт", "Корабль", "Самолет",
    "Поезд", "Такси", "Автобус", "Трамвай", "Троллейбус",
    "Лифт", "Подъезд", "Крыша", "Подвал", "Чердак",
    "Стройка", "Завод", "Фабрика", "Лаборатория",
    "Серверная", "IT-офис", "Хакерспейс", "Коворкинг",
    "Стрим-хата", "Студия", "Телестудия", "Радио",
    "Редакция", "Типография", "Почта", "Сортировка",
    "Архив", "Библиотечный зал", "Читальный зал",
    "Экзамен", "Контрольная", "Лекция", "Семинар",
    "Кафедра", "Деканат", "Общежитие", "Кухня",
    "Комната", "Балкон", "Двор", "Детская площадка"
]

# ===== KEYBOARDS =====
def watch_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👀 Посмотреть", callback_data="watch")]
        ]
    )

def next_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Следующий игрок", callback_data="next")]
        ]
    )

# ===== HANDLERS =====
@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.delete()
    await msg.answer(
        "Введите имена игроков через пробел\n"
        "Пример: Иван Макс Лера"
    )

@dp.message()
async def get_names(msg: Message):
    global players, roles, word, current_index

    players = msg.text.split()
    await msg.delete()

    word = random.choice(WORDS)
    spy = random.choice(players)

    roles = {}
    for p in players:
        roles[p] = "spy" if p == spy else word

    current_index = 0

    await msg.answer(
        f"📱 Передайте телефон игроку:\n\n<b>{players[current_index]}</b>",
        reply_markup=watch_kb()
    )

@dp.callback_query(F.data == "watch")
async def watch(cb):
    player = players[current_index]
    role = roles[player]

    await cb.message.edit_text(
        f"<b>{player}</b>\n\n"
        + ("🕵️ <b>Ты ШПИОН</b>" if role == "spy" else f"🔑 Твое слово: <b>{role}</b>")
        + "\n\n<i>✔ прочитано</i>",
        reply_markup=next_kb()
    )
    await cb.answer()

@dp.callback_query(F.data == "next")
async def next_player(cb):
    global current_index

    await cb.message.delete()
    current_index += 1

    if current_index < len(players):
        await cb.message.answer(
            f"📱 Передайте телефон игроку:\n\n<b>{players[current_index]}</b>",
            reply_markup=watch_kb()
        )
    else:
        await start_timer(cb.message.chat.id)

    await cb.answer()

# ===== TIMER =====
async def start_timer(chat_id):
    global video_message_id

    msg = await bot.send_video(
        chat_id=chat_id,
        video=open("timer.mp4", "rb"),
        caption="⏳ Игра началась"
    )
    video_message_id = msg.message_id

    await asyncio.sleep(180)

    await bot.delete_message(chat_id, video_message_id)
    await bot.send_message(chat_id, "🗳 Время вышло! Голосуйте")

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
