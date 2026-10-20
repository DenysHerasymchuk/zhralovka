from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import db
import screens
from i18n import detect_lang, t
from handlers.common import profile
from keyboards.menu import campus_keyboard, main_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    campus, lang = await profile(message.from_user)

    await screens.send(
        message,
        "hero",
        t(lang, "welcome", name=escape(message.from_user.first_name)),
        reply_markup=main_keyboard(lang) if campus else None,
    )

    if campus:
        await message.answer(t(lang, "welcome_back", campus=campus))
    else:
        await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard())


@router.message(Command("help"))
async def help_(message: Message):
    user = await db.get_user(message.from_user.id)
    lang = user[1] if user else detect_lang(message.from_user.language_code)
    await screens.send(message, "share", t(lang, "help"))
