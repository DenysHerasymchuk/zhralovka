import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
import screens
from handlers.common import profile
from i18n import all_langs, day_name, t
from keyboards.menu import campus_keyboard, main_keyboard, settings_keyboard
from menu.models import CAMPUSES

log = logging.getLogger(__name__)
router = Router()


def days_label(days: str, lang: str) -> str:
    return ", ".join(day_name(lang, int(d))[:2].capitalize() for d in sorted(days))


async def settings_view(user_id: int, campus: str | None, lang: str) -> dict:
    subscribed, hhmm, days = await db.get_notify(user_id)
    daily = f"{t(lang, 'daily_on')} · {hhmm} · {days_label(days, lang)}" if subscribed else t(lang, "daily_off")
    return {
        "text": t(lang, "settings", campus=campus or t(lang, "no_campus"), daily=daily),
        "reply_markup": settings_keyboard(lang, subscribed),
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

    _, lang = await profile(callback.from_user)
    await db.set_campus(callback.from_user.id, campus)
    log.info("User %s picked campus %s", callback.from_user.id, campus)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer(t(lang, "campus_saved", campus=campus), reply_markup=main_keyboard(lang))
    await callback.answer()


async def toggle_lang(message: Message, user) -> None:
    _, lang = await profile(user)
    lang = "nl" if lang == "en" else "en"
    await db.set_lang(user.id, lang)
    log.info("User %s switched to %s", user.id, lang)
    # A new message is the only way to swap the reply keyboard to the new language.
    await screens.send(message, "language", t(lang, "lang_saved"), reply_markup=main_keyboard(lang))


@router.message(Command("language"))
async def switch_lang(message: Message):
    await toggle_lang(message, message.from_user)


@router.callback_query(F.data == "settings:lang")
async def switch_lang_from_settings(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await toggle_lang(callback.message, callback.from_user)
    await callback.answer()
