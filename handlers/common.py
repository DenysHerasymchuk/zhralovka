import logging

from aiogram.types import User

import db
from i18n import detect_lang

log = logging.getLogger(__name__)


async def profile(user: User) -> tuple[str | None, str]:
    """(campus, lang), registering the user on first contact."""
    row = await db.get_user(user.id)
    if row:
        return row
    lang = detect_lang(user.language_code)
    await db.add_user(user.id, lang)
    log.info("New user %s, lang=%s", user.id, lang)
    return None, lang
