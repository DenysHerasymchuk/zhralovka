import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import db
from menu.models import DAYS, Dish, Week

WEEK = Week("Geel", date(2026, 10, 12), {
    day: [Dish("Soup", "Soep", "Leek soup", "Preisoep"), Dish("Lunch of the day", "Lunch van de dag", f"{day} pasta", "")]
    for day in DAYS
})
TUESDAY = date(2026, 10, 13)
SATURDAY = date(2026, 10, 17)


def message(text="", language_code="en"):
    msg = MagicMock()
    msg.text = text
    msg.from_user = SimpleNamespace(id=42, language_code=language_code, first_name="Sam")
    msg.answer = AsyncMock()
    return msg


def callback(data):
    cb = MagicMock()
    cb.data = data
    cb.from_user = SimpleNamespace(id=42, language_code="en")
    cb.message = message()
    cb.message.edit_text = AsyncMock()
    cb.message.delete = AsyncMock()
    cb.answer = AsyncMock()
    return cb


def sent_text(msg) -> str:
    return msg.answer.await_args.args[0]


class HandlerTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        await db.init(Path(self.tmp.name) / "test.db")

    async def asyncTearDown(self):
        self.tmp.cleanup()
