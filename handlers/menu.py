import re
from contextlib import suppress
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

from formatting import format_day, pick_day
from handlers.common import profile
from i18n import all_langs, day_name, t
from keyboards.menu import campus_keyboard, days_keyboard, day_nav_keyboard
from menu.client import MenuUnavailable, fetch_week
from menu.models import Week

TIMEZONE = ZoneInfo("Europe/Brussels")
# Dish names are links; without this Telegram previews the first one.
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

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
    return week, None


@router.message(Command("today"))
@router.message(F.text.in_(all_langs("btn_today")))
async def show_today(message: Message):
    campus, lang = await profile(message.from_user)
    if not campus:
        await message.answer(t(lang, "pick_campus"), reply_markup=campus_keyboard())
        return

    now = today()
    day, weekend = pick_day(now)
    if weekend:
        await message.answer(t(lang, "weekend", day=day_name(lang, now.weekday())))
        return

    week, problem = await load_week(campus, lang)
    if problem:
        await message.answer(problem)
        return
    await message.answer(
        format_day(week, day, lang, campus),
        reply_markup=day_nav_keyboard(day, lang),
        link_preview_options=NO_PREVIEW,
    )


@router.message(Command("week", "menu"))
@router.message(F.text.in_(all_langs("btn_week")))
async def show_week(message: Message):
    campus, lang = await profile(message.from_user)
    if not campus:
        await message.answer(t(lang, "pick_campus"), reply_markup=campus_keyboard())
        return

    week, problem = await load_week(campus, lang)
    if problem:
        await message.answer(problem)
        return

    day, _ = pick_day(today())
    await message.answer(
        format_day(week, day, lang, campus),
        reply_markup=days_keyboard(week.start, day, lang),
        link_preview_options=NO_PREVIEW,
    )


@router.callback_query(F.data.startswith(("day:", "nav:")))
async def switch_day(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    kind, _, day = callback.data.partition(":")
    if not campus or day not in {"0", "1", "2", "3", "4"}:
        await callback.answer()
        return
    day = int(day)

    week, problem = await load_week(campus, lang)
    if problem:
        await callback.answer(re.sub(r"<[^>]+>", "", problem), show_alert=True)
        return

    # Tapping the day that's already open raises "message is not modified".
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            format_day(week, day, lang, campus),
            reply_markup=days_keyboard(week.start, day, lang) if kind == "day" else day_nav_keyboard(day, lang),
            link_preview_options=NO_PREVIEW,
        )
    await callback.answer()
