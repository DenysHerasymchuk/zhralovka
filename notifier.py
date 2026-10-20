import asyncio
import logging
import time
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

import db
import screens
from config import TIMEZONE
from formatting import format_day
from keyboards.menu import day_nav_keyboard
from menu.client import MenuUnavailable, fetch_week
from menu.models import DAYS

# Telegram limit: ~30 messages per second.
SEND_INTERVAL = 0.05

log = logging.getLogger(__name__)


async def send_due(bot: Bot, day: int, hhmm: str) -> int:
    by_campus: dict[str, list[tuple[int, str]]] = {}
    for user_id, campus, lang in await db.subscribers_due(day, hhmm):
        by_campus.setdefault(campus, []).append((user_id, lang))
    if not by_campus:
        return 0

    sent = 0
    for campus, users in by_campus.items():
        try:
            week = await fetch_week(campus)
        except MenuUnavailable:
            log.warning("Daily menu skipped for %s: menu service unavailable", campus)
            continue
        if not week or not week.days[DAYS[day]]:
            continue

        for user_id, lang in users:
            try:
                await screens.send_to(
                    bot, user_id, "daily", format_day(week, day, lang, campus), reply_markup=day_nav_keyboard(day, lang)
                )
                sent += 1
            except TelegramForbiddenError:
                await db.set_subscribed(user_id, False)
                log.info("User %s blocked the bot, unsubscribed", user_id)
            except TelegramAPIError as exc:
                log.warning("Daily menu to %s failed: %r", user_id, exc)
            await asyncio.sleep(SEND_INTERVAL)

    log.info("Daily menu for %s sent to %d users", hhmm, sent)
    return sent


async def run(bot: Bot) -> None:
    while True:
        # +0.5s so an early wake-up can't read the previous minute.
        await asyncio.sleep(60 - time.time() % 60 + 0.5)
        now = datetime.now(TIMEZONE)
        if now.weekday() >= 5:
            continue
        try:
            await send_due(bot, now.weekday(), now.strftime("%H:%M"))
        except Exception:
            log.exception("Daily menu run failed")
