from aiogram import Router
from aiogram.types import Message

from handlers.common import profile
from i18n import t
from keyboards.menu import main_keyboard

router = Router()


@router.message()
async def fallback(message: Message):
    campus, lang = await profile(message.from_user)
    await message.answer(t(lang, "unknown"), reply_markup=main_keyboard(lang) if campus else None)
