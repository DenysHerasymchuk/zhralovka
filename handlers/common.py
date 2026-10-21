import logging

from aiogram.types import CallbackQuery, Chat, Message, ReplyKeyboardMarkup

import db
from i18n import detect_lang
from keyboards.menu import main_keyboard

log = logging.getLogger(__name__)


def _chat(event: Message | CallbackQuery) -> Chat | None:
    if isinstance(event, CallbackQuery):
        return event.message.chat if event.message else None
    return event.chat


def chat_id(event: Message | CallbackQuery) -> int:
    """The chat whose settings apply: the DM itself, or the group a button was tapped in."""
    chat = _chat(event)
    return chat.id if chat else event.from_user.id


def in_group(event: Message | CallbackQuery) -> bool:
    chat = _chat(event)
    return chat is not None and chat.type in ("group", "supergroup")


def reply_keyboard(event: Message | CallbackQuery, lang: str) -> ReplyKeyboardMarkup | None:
    """The bottom menu for DMs. Groups never get one: it would pop up for every member."""
    return None if in_group(event) else main_keyboard(lang)


async def profile(event: Message | CallbackQuery) -> tuple[str | None, str]:
    """(campus, lang) of the event's chat, registering the chat on first contact."""
    cid = chat_id(event)
    row = await db.get_user(cid)
    if row:
        return row
    lang = detect_lang(event.from_user.language_code)
    await db.add_user(cid, lang)
    log.info("New chat %s, lang=%s", cid, lang)
    return None, lang
