import asyncio
import logging
import time
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

import db
from config import DAILY_AT, TIMEZONE
from formatting import format_day
from handlers.menu import NO_PREVIEW
from keyboards.menu import day_nav_keyboard
from menu.client import MenuUnavailable, fetch_week
from menu.models import DAYS

# Telegram allows about 30 messages per second to different chats.
SEND_INTERVAL = 0.05

log = logging.getLogger(__name__)


def next_run(now: datetime) -> datetime:
    run = now.replace(hour=DAILY_AT.hour, minute=DAILY_AT.minute, second=0, microsecond=0)
    if run <= now:
        run += timedelta(days=1)
    while run.weekday() >= 5:
        run += timedelta(days=1)
    return run


async def send_daily(bot: Bot, day: int) -> int:
    by_campus: dict[str, list[tuple[int, str]]] = {}
    for user_id, campus, lang in await db.subscribers():
        by_campus.setdefault(campus, []).append((user_id, lang))

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
                await bot.send_message(
                    user_id,
                    format_day(week, day, lang, campus),
                    reply_markup=day_nav_keyboard(day, lang),
                    link_preview_options=NO_PREVIEW,
                )
                sent += 1
            except TelegramForbiddenError:
                await db.set_subscribed(user_id, False)
                log.info("User %s blocked the bot, unsubscribed", user_id)
            except TelegramAPIError as exc:
                log.warning("Daily menu to %s failed: %r", user_id, exc)
            await asyncio.sleep(SEND_INTERVAL)

    log.info("Daily menu sent to %d users", sent)
    return sent


async def run(bot: Bot) -> None:
    while True:
        target = next_run(datetime.now(TIMEZONE))
        log.info("Next daily menu at %s", target.isoformat(timespec="minutes"))
        # Timestamps, not datetime subtraction, so DST changes don't shift the send by an hour.
        await asyncio.sleep(max(0, target.timestamp() - time.time()))
        try:
            await send_daily(bot, target.weekday())
        except Exception:
            log.exception("Daily menu run failed")
