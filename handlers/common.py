import logging

from aiogram.types import CallbackQuery, Message

import db
from i18n import detect_lang

log = logging.getLogger(__name__)


def chat_id(event: Message | CallbackQuery) -> int:
    """The chat whose settings apply: the DM itself, or the group a button was tapped in."""
    if isinstance(event, CallbackQuery):
        return event.message.chat.id if event.message else event.from_user.id
    return event.chat.id


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
