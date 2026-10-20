from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import db
from handlers.common import profile
from i18n import all_langs, t
from keyboards.menu import campus_keyboard, main_keyboard, settings_keyboard
from menu.models import CAMPUSES

router = Router()


@router.message(F.text.in_(all_langs("btn_settings")))
async def show_settings(message: Message):
    campus, lang = await profile(message.from_user)
    await message.answer(
        t(lang, "settings", campus=campus or t(lang, "no_campus")),
        reply_markup=settings_keyboard(lang),
    )


@router.message(Command("campus"))
async def ask_campus(message: Message):
    campus, lang = await profile(message.from_user)
    await message.answer(t(lang, "pick_campus"), reply_markup=campus_keyboard(campus))


@router.callback_query(F.data == "settings:campus")
async def ask_campus_from_settings(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    await callback.message.edit_text(t(lang, "pick_campus"), reply_markup=campus_keyboard(campus))
    await callback.answer()


@router.callback_query(F.data.startswith("campus:"))
async def save_campus(callback: CallbackQuery):
    campus = callback.data.removeprefix("campus:")
    if campus not in CAMPUSES:
        await callback.answer()
        return

    _, lang = await profile(callback.from_user)
    await db.set_campus(callback.from_user.id, campus)
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await callback.message.answer(t(lang, "campus_saved", campus=campus), reply_markup=main_keyboard(lang))
    await callback.answer()


async def toggle_lang(message: Message, user) -> None:
    _, lang = await profile(user)
    lang = "nl" if lang == "en" else "en"
    await db.set_lang(user.id, lang)
    # A new message is the only way to swap the reply keyboard to the new language.
    await message.answer(t(lang, "lang_saved"), reply_markup=main_keyboard(lang))


@router.message(Command("language"))
async def switch_lang(message: Message):
    await toggle_lang(message, message.from_user)


@router.callback_query(F.data == "settings:lang")
async def switch_lang_from_settings(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.message.delete()
    await toggle_lang(callback.message, callback.from_user)
    await callback.answer()
