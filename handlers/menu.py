import re
from contextlib import suppress
from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
import screens
from config import TIMEZONE
from formatting import format_day, pick_day
from handlers.common import chat_id, profile
from i18n import all_langs, day_name, t
from keyboards.menu import campus_keyboard, days_keyboard, day_nav_keyboard
from menu.client import MenuUnavailable, fetch_week
from menu.models import Week, covers
from menu.translate import localize

router = Router()


def today():
    return datetime.now(TIMEZONE).date()


async def load_week(campus: str, lang: str) -> tuple[Week | None, str | None]:
    try:
        week = await fetch_week(campus)
    except MenuUnavailable:
        return None, t(lang, "unavailable")
    if week is None:
        return None, t(lang, "no_menu", campus=campus)
    return await localize(week, lang), None


@router.message(Command("today", "menu"))
@router.message(F.text.in_(all_langs("btn_today")))
async def show_today(message: Message):
    campus, lang = await profile(message)
    if not campus:
        await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard())
        return

    now = today()
    day, weekend = pick_day(now)
    if weekend:
        await message.answer(t(lang, "weekend", day=day_name(lang, now.weekday())))
        return

    week, problem = await load_week(campus, lang)
    if not problem and not covers(week, now):
        problem = t(lang, "no_menu", campus=campus)
    if problem:
        await message.answer(problem)
        return
    prices = await db.get_show_prices(chat_id(message))
    await screens.send(message, "today", format_day(week, day, lang, campus, prices), reply_markup=day_nav_keyboard(day, lang))


@router.message(Command("week"))
@router.message(F.text.in_(all_langs("btn_week")))
async def show_week(message: Message):
    campus, lang = await profile(message)
    if not campus:
        await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard())
        return

    week, problem = await load_week(campus, lang)
    if problem:
        await message.answer(problem)
        return

    day, _ = pick_day(today())
    prices = await db.get_show_prices(chat_id(message))
    await screens.send(
        message, "thisweek", format_day(week, day, lang, campus, prices), reply_markup=days_keyboard(week.start, day, lang)
    )


@router.callback_query(F.data.startswith(("day:", "nav:")))
async def switch_day(callback: CallbackQuery):
    campus, lang = await profile(callback)
    kind, _, day = callback.data.partition(":")
    if not campus or day not in {"0", "1", "2", "3", "4"}:
        await callback.answer()
        return
    day = int(day)
    prices = await db.get_show_prices(chat_id(callback))

    week, problem = await load_week(campus, lang)
    if problem:
        await callback.answer(re.sub(r"<[^>]+>", "", problem), show_alert=True)
        return

    if kind == "day":
        markup, picture = days_keyboard(week.start, day, lang), None
    else:
        # Stepping off today in the Today view turns it into a week browser.
        markup = day_nav_keyboard(day, lang)
        picture = "today" if day == today().weekday() else "thisweek"

    # Tapping the day that's already open raises "message is not modified".
    with suppress(TelegramBadRequest):
        await screens.edit(callback.message, format_day(week, day, lang, campus, prices), reply_markup=markup, picture=picture)
    await callback.answer()
