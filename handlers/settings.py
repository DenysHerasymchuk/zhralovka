import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
import screens
from handlers.common import admin_only, chat_id, in_group, profile, reply_keyboard
from i18n import LANGS, all_langs, day_short, t
from keyboards.menu import campus_keyboard, language_keyboard, settings_keyboard
from menu.models import CAMPUSES

log = logging.getLogger(__name__)
router = Router()


def days_label(days: str, lang: str) -> str:
    return ", ".join(day_short(lang, int(d)) for d in sorted(days))


async def settings_view(cid: int, campus: str | None, lang: str) -> dict:
    subscribed, hhmm, days = await db.get_notify(cid)
    show_prices = await db.get_show_prices(cid)
    daily = f"{t(lang, 'daily_on')} · {hhmm} · {days_label(days, lang)}" if subscribed else t(lang, "daily_off")
    prices = t(lang, "daily_on" if show_prices else "daily_off")
    return {
        "text": t(lang, "settings", campus=campus or t(lang, "no_campus"), daily=daily, prices=prices),
        "reply_markup": settings_keyboard(lang, subscribed, show_prices),
    }


@router.message(Command("settings"))
@router.message(F.text.in_(all_langs("btn_settings")))
async def show_settings(message: Message):
    campus, lang = await profile(message)
    if not await admin_only(message, lang):
        return
    await screens.send(message, "settings", **await settings_view(chat_id(message), campus, lang))


@router.message(Command("campus"))
async def ask_campus(message: Message):
    campus, lang = await profile(message)
    if not await admin_only(message, lang):
        return
    await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard(campus))


@router.callback_query(F.data == "settings:campus")
async def ask_campus_from_settings(callback: CallbackQuery):
    campus, lang = await profile(callback)
    if not await admin_only(callback, lang):
        return
    await screens.edit(callback.message, t(lang, "pick_campus"), reply_markup=campus_keyboard(campus), picture="location")
    await callback.answer()


@router.callback_query(F.data.startswith("campus:"))
async def save_campus(callback: CallbackQuery):
    campus = callback.data.removeprefix("campus:")
    if campus not in CAMPUSES:
        await callback.answer()
        return

    previous, lang = await profile(callback)
    if not await admin_only(callback, lang):
        return
    await db.set_campus(chat_id(callback), campus)
    log.info("Chat %s picked campus %s", chat_id(callback), campus)
    if previous:
        await screens.edit(callback.message, **await settings_view(chat_id(callback), campus, lang), picture="settings")
    else:
        # A first-time user has no bottom keyboard yet, and only a new message can add one.
        with suppress(TelegramBadRequest):
            await callback.message.delete()
        if in_group(callback):
            await callback.message.answer(t(lang, "campus_saved_group", campus=campus))
        else:
            await callback.message.answer(t(lang, "campus_saved", campus=campus), reply_markup=reply_keyboard(callback, lang))
    await callback.answer()


@router.message(Command("language"))
async def ask_lang(message: Message):
    _, lang = await profile(message)
    if not await admin_only(message, lang):
        return
    await message.answer(t(lang, "pick_lang"), reply_markup=language_keyboard(lang))


@router.callback_query(F.data == "settings:lang")
async def ask_lang_from_settings(callback: CallbackQuery):
    _, lang = await profile(callback)
    if not await admin_only(callback, lang):
        return
    await screens.edit(callback.message, t(lang, "pick_lang"), reply_markup=language_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def save_lang(callback: CallbackQuery):
    lang = callback.data.removeprefix("lang:")
    if lang not in LANGS:
        await callback.answer()
        return
    campus, current = await profile(callback)
    if not await admin_only(callback, current):
        return
    await db.set_lang(chat_id(callback), lang)
    log.info("Chat %s switched to %s", chat_id(callback), lang)
    await screens.edit(callback.message, **await settings_view(chat_id(callback), campus, lang))
    # A new message is the only way to swap the bottom keyboard to the new language. Groups have none.
    if not in_group(callback):
        await callback.message.answer(t(lang, "lang_saved"), reply_markup=reply_keyboard(callback, lang))
    await callback.answer()


@router.callback_query(F.data == "settings:prices")
async def toggle_prices(callback: CallbackQuery):
    campus, lang = await profile(callback)
    if not await admin_only(callback, lang):
        return
    show = not await db.get_show_prices(chat_id(callback))
    await db.set_show_prices(chat_id(callback), show)
    log.info("Chat %s turned menu prices %s", chat_id(callback), "on" if show else "off")
    await screens.edit(callback.message, **await settings_view(chat_id(callback), campus, lang))
    await callback.answer()
