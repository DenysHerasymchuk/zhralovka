import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from handlers.common import admin_only, chat_id, in_group, profile
from i18n import t

log = logging.getLogger(__name__)
router = Router()


@router.message(Command("clear"))
async def clear(message: Message):
    _, lang = await profile(message)
    if not await admin_only(message, lang):
        return
    # Telegram only drops a reply keyboard when a message tells it to, so this sends one.
    text = t(lang, "menu_cleared_group" if in_group(message) else "menu_cleared")
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    log.info("Chat %s cleared the bottom menu", chat_id(message))
