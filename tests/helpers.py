import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import CallbackQuery, Message

import db
from menu.models import DAYS, Dish, Week

WEEK = Week("Geel", date(2026, 10, 12), {
    day: [Dish("Soup", "Soep", "Leek soup", "Preisoep"), Dish("Lunch of the day", "Lunch van de dag", f"{day} pasta", "")]
    for day in DAYS
})
TUESDAY = date(2026, 10, 13)
SATURDAY = date(2026, 10, 17)


def message(text="", language_code="en", user_id=42, chat_id=None, chat_type="private"):
    """A message from user_id; in a private chat (the default) the chat id is the user id."""
    msg = MagicMock(spec=Message)  # spec, so isinstance(msg, Message) holds
    msg.text = text
    msg.photo = None
    msg.from_user = SimpleNamespace(id=user_id, language_code=language_code, first_name="Sam")
    msg.chat = SimpleNamespace(id=user_id if chat_id is None else chat_id, type=chat_type)
    msg.answer = AsyncMock()
    msg.answer_photo = AsyncMock()
    return msg


def callback(data, user_id=42, chat_id=None, chat_type="private"):
    """A button tap by user_id on a message in chat_id (the user's own DM by default)."""
    cb = MagicMock(spec=CallbackQuery)
    cb.data = data
    cb.from_user = SimpleNamespace(id=user_id, language_code="en")
    cb.message = message(user_id=user_id, chat_id=chat_id, chat_type=chat_type)
    cb.message.edit_text = AsyncMock()
    cb.message.delete = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def last_sent(msg) -> tuple[str, dict]:
    """(text or caption, other kwargs) of the latest answer() or answer_photo()."""
    name, args, kwargs = next(c for c in reversed(msg.mock_calls) if c[0] in ("answer", "answer_photo"))
    kwargs = dict(kwargs)
    if name == "answer_photo":
        return kwargs.pop("caption"), {"picture": args[0], **kwargs}
    return args[0], kwargs


def sent_text(msg) -> str:
    return last_sent(msg)[0]


def sent_markup(msg):
    return last_sent(msg)[1]["reply_markup"]


def sent_picture(msg) -> str:
    return Path(last_sent(msg)[1]["picture"].path).stem


class HandlerTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        await db.init(Path(self.tmp.name) / "test.db")
        # A real DEEPL_API_KEY in a developer's .env must not make tests call DeepL.
        patcher = patch("menu.translate.DEEPL_API_KEY", "")
        patcher.start()
        self.addCleanup(patcher.stop)

    async def asyncTearDown(self):
        self.tmp.cleanup()
