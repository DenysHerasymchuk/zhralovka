from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import screens
from handlers.common import profile, reply_keyboard
from i18n import t
from keyboards.menu import campus_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    campus, lang = await profile(message)

    await screens.send(
        message,
        "hero",
        t(lang, "welcome", name=escape(message.from_user.first_name)),
        reply_markup=reply_keyboard(message, lang) if campus else None,
    )

    if campus:
        await message.answer(t(lang, "welcome_back", campus=campus))
    else:
        await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard())


@router.message(Command("help"))
async def help_(message: Message):
    _, lang = await profile(message)
    await screens.send(message, "share", t(lang, "help"))
