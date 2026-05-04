import os
import json
import random
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

ADMIN_ID = 1865648570

DATA_DIR = os.getenv("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

LINKS_FILE = os.path.join(DATA_DIR, "links.json")
CODES_FILE = os.path.join(DATA_DIR, "codes.json")


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Аккаунт"), KeyboardButton(text="🪙 Ded коины")],
        [KeyboardButton(text="🎮 Онлайн"), KeyboardButton(text="🌐 Ссылки DedRP")]
    ],
    resize_keyboard=True
)

link_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 Привязать Minecraft аккаунт")]
    ],
    resize_keyboard=True
)


def get_linked_player(telegram_id: int):
    links = load_json(LINKS_FILE)
    return links.get(str(telegram_id))


@dp.message(Command("start"))
async def start(message: types.Message):
    player = get_linked_player(message.from_user.id)

    if not player:
        await message.answer(
            "❌ Ты не привязан к Minecraft аккаунту.\n\n"
            "Нажми кнопку ниже:",
            reply_markup=link_menu
        )
        return

    await message.answer(
        f"👋 Добро пожаловать в DedRP\n\n"
        f"✅ Привязан аккаунт: {player}",
        reply_markup=main_menu
    )


@dp.message(Command("id"))
async def my_id(message: types.Message):
    await message.answer(f"Твой Telegram ID: {message.from_user.id}")


@dp.message(Command("testcode"))
async def test_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет доступа")
        return

    args = message.text.split()

    if len(args) != 2:
        await message.answer("Использование: /testcode ник")
        return

    nickname = args[1]
    code = str(random.randint(100000, 999999))

    codes = load_json(CODES_FILE)
    codes[code] = nickname
    save_json(CODES_FILE, codes)

    await message.answer(
        f"✅ Тестовый код создан\n\n"
        f"Ник: {nickname}\n"
        f"Код: {code}\n\n"
        f"Игрок должен написать:\n"
        f"/link {code}"
    )


@dp.message(Command("link"))
async def link_account(message: types.Message):
    args = message.text.split()

    if len(args) != 2:
        await message.answer("❌ Использование: /link код")
        return

    code = args[1]

    codes = load_json(CODES_FILE)

    if code not in codes:
        await message.answer("❌ Код не найден или уже использован")
        return

    nickname = codes[code]

    links = load_json(LINKS_FILE)
    links[str(message.from_user.id)] = nickname

    del codes[code]

    save_json(LINKS_FILE, links)
    save_json(CODES_FILE, codes)

    await message.answer(
        f"✅ Аккаунт успешно привязан!\n\n"
        f"Minecraft ник: {nickname}",
        reply_markup=main_menu
    )


@dp.message()
async def menu_handler(message: types.Message):
    text = message.text
    player = get_linked_player(message.from_user.id)

    if text == "🔗 Привязать Minecraft аккаунт":
        await message.answer(
            "📌 Как привязать аккаунт:\n\n"
            "1. Зайди на сервер DedRP\n"
            "2. Напиши /привязать\n"
            "3. Получи код\n"
            "4. Напиши сюда: /link код\n\n"
            "Пока серверная команда не подключена, админ может создать тестовый код через /testcode ник"
        )
        return

    if not player:
        await message.answer(
            "❌ Сначала привяжи Minecraft аккаунт.",
            reply_markup=link_menu
        )
        return

    if text == "👤 Аккаунт":
        await message.answer(
            f"👤 Аккаунт\n\n"
            f"✅ Привязан ник: {player}\n\n"
            f"🚪 Отключение с сервера — скоро\n"
            f"🔑 Смена пароля — скоро\n"
            f"🔒 Блокировка аккаунта — скоро"
        )

    elif text == "🪙 Ded коины":
        await message.answer(
            "🪙 Ded коины\n\n"
            "💰 Баланс — скоро\n"
            "🔁 Переводы — скоро\n"
            "📜 История — скоро"
        )

    elif text == "🎮 Онлайн":
        await message.answer(
            "🎮 Онлайн режимов\n\n"
            "🏚 Выживание бомжа — скоро\n"
            "🌌 Выживание Nexus — скоро"
        )

    elif text == "🌐 Ссылки DedRP":
        await message.answer(
            "🌐 Официальные ссылки DedRP:\n\n"
            "💬 Telegram группа: @DedRPone\n"
            "🌍 Сайт: https://dedrp.online\n"
            "🎧 Discord: https://discord.gg/QvWAMr6Nr2\n"
            "📜 Правила сервера: https://dedrp.online/rules"
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
 
