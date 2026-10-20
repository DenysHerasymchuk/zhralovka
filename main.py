import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

import db
from config import API_TOKEN
from handlers.fallback import router as fallback_router
from handlers.menu import router as menu_router
from handlers.settings import router as settings_router
from handlers.start import router as start_router
from i18n import LANGS, t

COMMANDS = ("today", "week", "campus", "language", "help", "start")

dp = Dispatcher()
# fallback_router catches every message, so it goes last.
dp.include_routers(start_router, settings_router, menu_router, fallback_router)


async def set_commands(bot: Bot) -> None:
    for lang in LANGS:
        await bot.set_my_commands(
            [BotCommand(command=cmd, description=t(lang, f"cmd_{cmd}")) for cmd in COMMANDS],
            language_code=None if lang == "en" else lang,
        )


async def main():
    if not API_TOKEN:
        raise RuntimeError("API_TOKEN is missing. Copy .env.example to .env and add your bot token.")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    await db.init()

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    await set_commands(bot)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
