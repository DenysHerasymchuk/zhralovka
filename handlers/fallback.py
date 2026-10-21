from aiogram import Router
from aiogram.types import Message

from handlers.common import in_group, profile, reply_keyboard
from i18n import t

router = Router()


@router.message()
async def fallback(message: Message):
    # In a group this would answer chatter and other bots' commands, so stay quiet there.
    if in_group(message):
        return
    campus, lang = await profile(message)
    await message.answer(t(lang, "unknown"), reply_markup=reply_keyboard(message, lang) if campus else None)
