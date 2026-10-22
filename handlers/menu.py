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
from formatting import format_day, format_hot_meal, pick_day
from handlers.common import button_command, campus_prompt, chat_id, may_use, profile
from i18n import all_langs, day_name, t
from keyboards.menu import campus_keyboard, days_keyboard, day_nav_keyboard
from menu.client import MenuUnavailable, fetch_week
from menu.models import Week, covers
from menu.translate import localize
from screens import NO_PREVIEW

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


async def load_today(campus: str, lang: str) -> tuple[Week | None, int, str | None]:
    """(week, today's index, None), or a message saying why there's no menu today."""
    now = today()
    day, weekend = pick_day(now)
    if weekend:
        return None, day, t(lang, "weekend", day=day_name(lang, now.weekday()))
    week, problem = await load_week(campus, lang)
    if not problem and not covers(week, now):
        problem = t(lang, "no_menu", campus=campus)
    return week, day, problem


@router.message(Command("today", "menu"))
@router.message(F.text.in_(all_langs("btn_today")))
async def show_today(message: Message):
    campus, lang = await profile(message)
    if not await may_use(message, "today", lang):
        return
    if not campus:
        await screens.send(message, "location", campus_prompt(message, lang), reply_markup=campus_keyboard())
        return

    week, day, problem = await load_today(campus, lang)
    if problem:
        await message.answer(problem)
        return
    prices = await db.get_show_prices(chat_id(message))
    await screens.send(message, "today", format_day(week, day, lang, campus, prices), reply_markup=day_nav_keyboard(day, lang))


@router.message(Command("shortm"))
async def show_hot_meal(message: Message):
    """Today's hot meal as a text reply with day buttons: no picture, no link preview."""
    campus, lang = await profile(message)
    if not await may_use(message, "shortm", lang):
        return
    if not campus:
        await screens.send(message, "location", campus_prompt(message, lang), reply_markup=campus_keyboard())
        return

    week, day, problem = await load_today(campus, lang)
    if problem:
        await message.reply(problem)
        return
    prices = await db.get_show_prices(chat_id(message))
    await message.reply(
        format_hot_meal(week, day, lang, campus, prices),
        reply_markup=day_nav_keyboard(day, lang, "hot"),
        link_preview_options=NO_PREVIEW,
    )


@router.callback_query(F.data.startswith("hot:"))
async def switch_hot_meal(callback: CallbackQuery):
    """⬅️/➡️ under /shortm: the same message, another day's hot meal."""
    campus, lang = await profile(callback)
    if not await may_use(callback, button_command(callback), lang):
        return
    day = callback.data.removeprefix("hot:")
    if not campus or day not in {"0", "1", "2", "3", "4"}:
        await callback.answer()
        return
    day = int(day)

    week, problem = await load_week(campus, lang)
    if problem:
        await callback.answer(re.sub(r"<[^>]+>", "", problem), show_alert=True)
        return
    prices = await db.get_show_prices(chat_id(callback))
    with suppress(TelegramBadRequest):
        await screens.edit(callback.message, format_hot_meal(week, day, lang, campus, prices), reply_markup=day_nav_keyboard(day, lang, "hot"))
    await callback.answer()


@router.message(Command("week"))
@router.message(F.text.in_(all_langs("btn_week")))
async def show_week(message: Message):
    campus, lang = await profile(message)
    if not await may_use(message, "week", lang):
        return
    if not campus:
        await screens.send(message, "location", campus_prompt(message, lang), reply_markup=campus_keyboard())
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
    if not await may_use(callback, button_command(callback), lang):
        return
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
