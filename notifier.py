import asyncio
import logging
import time
from datetime import date, datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramMigrateToChat

import db
import screens
from config import TIMEZONE
from formatting import format_day
from keyboards.menu import day_nav_keyboard
from menu.client import NEW_WEEK_AT, MenuUnavailable, fetch_week
from menu.models import DAYS, Week, covers
from menu.translate import localize, prewarm

# Telegram limit: ~30 messages per second.
SEND_INTERVAL = 0.05

log = logging.getLogger(__name__)


async def send_due(bot: Bot, today: date, hhmm: str) -> int:
    day = today.weekday()
    by_campus: dict[str, list[tuple[int, str, bool]]] = {}
    for chat, campus, lang, prices in await db.subscribers_due(day, hhmm):
        by_campus.setdefault(campus, []).append((chat, lang, bool(prices)))
    if not by_campus:
        return 0

    sent = 0
    for campus, chats in by_campus.items():
        try:
            week = await fetch_week(campus)
        except MenuUnavailable:
            log.warning("Daily menu skipped for %s: menu service unavailable", campus)
            continue
        if not week or not covers(week, today) or not week.days[DAYS[day]]:
            log.info("Daily menu skipped for %s: no menu for today yet", campus)
            continue

        localized: dict[str, Week] = {}
        for chat, lang, prices in chats:
            if lang not in localized:
                localized[lang] = await localize(week, lang)
            text = format_day(localized[lang], day, lang, campus, prices)
            markup = day_nav_keyboard(day, lang)
            try:
                try:
                    await screens.send_to(bot, chat, "daily", text, reply_markup=markup)
                except TelegramMigrateToChat as moved:
                    # The group became a supergroup since it subscribed; follow it to the new id.
                    await db.move_chat(chat, moved.migrate_to_chat_id)
                    await screens.send_to(bot, moved.migrate_to_chat_id, "daily", text, reply_markup=markup)
                sent += 1
            except TelegramForbiddenError:
                await db.set_subscribed(chat, False)
                log.info("Chat %s blocked or removed the bot, unsubscribed", chat)
            except TelegramAPIError as exc:
                log.warning("Daily menu to %s failed: %r", chat, exc)
            await asyncio.sleep(SEND_INTERVAL)

    log.info("Daily menu for %s sent to %d chats", hhmm, sent)
    return sent


async def run(bot: Bot) -> None:
    while True:
        # +0.5s so an early wake-up can't read the previous minute.
        await asyncio.sleep(60 - time.time() % 60 + 0.5)
        now = datetime.now(TIMEZONE)
        # The new week is due Monday at NEW_WEEK_AT; translate it then. Later changes are translated on first view.
        if now.weekday() == 0 and now.strftime("%H:%M") == NEW_WEEK_AT.strftime("%H:%M"):
            try:
                await prewarm()
            except Exception:
                log.exception("Translation prewarm failed")
        if now.weekday() >= 5:
            continue
        try:
            await send_due(bot, now.date(), now.strftime("%H:%M"))
        except Exception:
            log.exception("Daily menu run failed")
