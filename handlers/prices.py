from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import screens
from formatting import format_prices
from handlers.common import profile
from keyboards.menu import prices_keyboard
from menu.prices import SECTIONS

router = Router()


@router.message(Command("prices", "price"))
async def show_prices(message: Message):
    _, lang = await profile(message)
    await screens.send(message, "menu", format_prices(0, lang), reply_markup=prices_keyboard(0))


@router.callback_query(F.data.startswith("prices:"))
async def switch_section(callback: CallbackQuery):
    choice = callback.data.removeprefix("prices:")
    if choice not in {str(i) for i in range(len(SECTIONS))}:
        await callback.answer()
        return
    section = int(choice)
    _, lang = await profile(callback)
    # Tapping the open section raises "message is not modified".
    with suppress(TelegramBadRequest):
        await screens.edit(callback.message, format_prices(section, lang), reply_markup=prices_keyboard(section))
    await callback.answer()
