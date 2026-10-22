import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

import db
import notifier
from commands import set_commands
from config import API_TOKEN, LOG_LEVEL
from handlers.clear import router as clear_router
from handlers.fallback import router as fallback_router
from handlers.groups import router as groups_router
from handlers.menu import router as menu_router
from handlers.notify import router as notify_router
from handlers.prices import router as prices_router
from handlers.settings import router as settings_router
from handlers.start import router as start_router
from middleware import log_updates

log = logging.getLogger("bot")

dp = Dispatcher()
dp.update.outer_middleware(log_updates)
# Order matters: notify after menu so menu buttons beat a pending time prompt; fallback last.
dp.include_routers(
    groups_router,
    start_router,
    settings_router,
    menu_router,
    prices_router,
    clear_router,
    notify_router,
    fallback_router,
)


async def main():
    if not API_TOKEN:
        raise RuntimeError("API_TOKEN is missing. Copy .env.example to .env and add your bot token.")

    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    await db.init()
    log.info("Database ready at %s", db.DB_PATH)

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    me = await bot.get_me()
    await set_commands(bot)
    log.info("Starting @%s", me.username)
    daily = asyncio.create_task(notifier.run(bot))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        daily.cancel()


if __name__ == "__main__":
    asyncio.run(main())
