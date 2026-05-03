import os
import asyncio
import aiomysql

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token="8602098873:AAHUcMSLJk7G7p16hXRUfDumcaRV1QecFkc")
dp = Dispatcher()


# ===== МЕНЮ =====

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


# ===== БАЗА =====

async def get_db():
    return await aiomysql.connect(
        host="localhost",
        user="root",
        password="",
        db="dedrp",
        autocommit=False
    )


async def get_player_by_telegram(telegram_id: int):
    conn = await get_db()

    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "SELECT * FROM coin_accounts WHERE telegram_id=%s",
            (telegram_id,)
        )
        player = await cur.fetchone()

    conn.close()
    return player


# ===== START =====

@dp.message(Command("start"))
async def start(message: types.Message):
    player = await get_player_by_telegram(message.from_user.id)

    if not player:
        await message.answer(
            "❌ Ты не привязан к аккаунту\n\n"
            "Нажми кнопку ниже:",
            reply_markup=link_menu
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в DedRP",
            reply_markup=main_menu
        )


# ===== LINK =====

@dp.message(Command("link"))
async def link_account(message: types.Message):
    args = message.text.split()

    if len(args) != 2:
        await message.answer("❌ Использование: /link код")
        return

    code = args[1]

    conn = await get_db()

    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            await cur.execute(
                "SELECT * FROM account_links WHERE code=%s AND used=FALSE",
                (code,)
            )
            link = await cur.fetchone()

            if not link:
                await message.answer("❌ Код не найден или уже использован")
                return

            nickname = link["nickname"]

            await cur.execute(
                "UPDATE coin_accounts SET telegram_id=%s WHERE nickname=%s",
                (message.from_user.id, nickname)
            )

            await cur.execute(
                "UPDATE account_links SET used=TRUE WHERE code=%s",
                (code,)
            )

            await conn.commit()

        await message.answer(
            f"✅ Аккаунт {nickname} привязан!",
            reply_markup=main_menu
        )

    except Exception as e:
        await conn.rollback()
        await message.answer("❌ Ошибка привязки")
        print(e)

    finally:
        conn.close()


# ===== КНОПКИ =====

@dp.message()
async def menu_handler(message: types.Message):
    text = message.text

    if text == "🔗 Привязать Minecraft аккаунт":
        await message.answer(
            "📌 Как привязать:\n\n"
            "1. Зайди на сервер\n"
            "2. Напиши /привязать\n"
            "3. Получи код\n"
            "4. Напиши сюда: /link код"
        )

    elif text == "🌐 Ссылки DedRP":
        await message.answer(
            "🌐 Ссылки DedRP:\n\n"
            "💬 Telegram: @DedRPone\n"
            "🌍 Сайт: https://dedrp.online\n"
            "🎧 Discord: https://discord.gg/QvWAMr6Nr2\n"
            "📜 Правила: https://dedrp.online/rules"
        )


# ===== ЗАПУСК =====

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())