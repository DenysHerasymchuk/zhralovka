import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
import screens
from handlers.common import profile
from i18n import LANGS, all_langs, day_short, t
from keyboards.menu import campus_keyboard, language_keyboard, main_keyboard, settings_keyboard
from menu.models import CAMPUSES

log = logging.getLogger(__name__)
router = Router()


def days_label(days: str, lang: str) -> str:
    return ", ".join(day_short(lang, int(d)) for d in sorted(days))


async def settings_view(user_id: int, campus: str | None, lang: str) -> dict:
    subscribed, hhmm, days = await db.get_notify(user_id)
    show_prices = await db.get_show_prices(user_id)
    daily = f"{t(lang, 'daily_on')} · {hhmm} · {days_label(days, lang)}" if subscribed else t(lang, "daily_off")
    prices = t(lang, "daily_on" if show_prices else "daily_off")
    return {
        "text": t(lang, "settings", campus=campus or t(lang, "no_campus"), daily=daily, prices=prices),
        "reply_markup": settings_keyboard(lang, subscribed, show_prices),
    }


@router.message(F.text.in_(all_langs("btn_settings")))
async def show_settings(message: Message):
    campus, lang = await profile(message.from_user)
    await screens.send(message, "settings", **await settings_view(message.from_user.id, campus, lang))


@router.message(Command("campus"))
async def ask_campus(message: Message):
    campus, lang = await profile(message.from_user)
    await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard(campus))


@router.callback_query(F.data == "settings:campus")
async def ask_campus_from_settings(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    await screens.edit(callback.message, t(lang, "pick_campus"), reply_markup=campus_keyboard(campus), picture="location")
    await callback.answer()


@router.callback_query(F.data.startswith("campus:"))
async def save_campus(callback: CallbackQuery):
    campus = callback.data.removeprefix("campus:")
    if campus not in CAMPUSES:
        await callback.answer()
        return

    previous, lang = await profile(callback.from_user)
    await db.set_campus(callback.from_user.id, campus)
    log.info("User %s picked campus %s", callback.from_user.id, campus)
    if previous:
        await screens.edit(callback.message, **await settings_view(callback.from_user.id, campus, lang), picture="settings")
    else:
        # A first-time user has no bottom keyboard yet, and only a new message can add one.
        with suppress(TelegramBadRequest):
            await callback.message.delete()
        await callback.message.answer(t(lang, "campus_saved", campus=campus), reply_markup=main_keyboard(lang))
    await callback.answer()


@router.message(Command("language"))
async def ask_lang(message: Message):
    _, lang = await profile(message.from_user)
    await message.answer(t(lang, "pick_lang"), reply_markup=language_keyboard(lang))


@router.callback_query(F.data == "settings:lang")
async def ask_lang_from_settings(callback: CallbackQuery):
    _, lang = await profile(callback.from_user)
    await screens.edit(callback.message, t(lang, "pick_lang"), reply_markup=language_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def save_lang(callback: CallbackQuery):
    lang = callback.data.removeprefix("lang:")
    if lang not in LANGS:
        await callback.answer()
        return
    campus, _ = await profile(callback.from_user)
    await db.set_lang(callback.from_user.id, lang)
    log.info("User %s switched to %s", callback.from_user.id, lang)
    await screens.edit(callback.message, **await settings_view(callback.from_user.id, campus, lang))
    # A new message is the only way to swap the bottom keyboard to the new language.
    await callback.message.answer(t(lang, "lang_saved"), reply_markup=main_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "settings:prices")
async def toggle_prices(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    show = not await db.get_show_prices(callback.from_user.id)
    await db.set_show_prices(callback.from_user.id, show)
    log.info("User %s turned menu prices %s", callback.from_user.id, "on" if show else "off")
    await screens.edit(callback.message, **await settings_view(callback.from_user.id, campus, lang))
    await callback.answer()
