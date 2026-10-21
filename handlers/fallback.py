from aiogram import Router
from aiogram.types import Message

from handlers.common import profile, reply_keyboard
from i18n import t

router = Router()


@router.message()
async def fallback(message: Message):
    campus, lang = await profile(message)
    await message.answer(t(lang, "unknown"), reply_markup=reply_keyboard(message, lang) if campus else None)
