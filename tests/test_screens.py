import re
import unittest
from html import unescape
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import Message

import screens
from formatting import format_day
from menu.models import parse_week
from tests.helpers import message

FIXTURE = (Path(__file__).parent / "fixtures" / "geel.json").read_text()
CAPTION_LIMIT = 1024


def sent_photo(file_id):
    sent = MagicMock(spec=Message)
    sent.photo = [MagicMock(file_id=file_id)]
    return sent


class SendTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        screens._file_ids.clear()

    async def test_second_send_reuses_file_id(self):
        msg = message()
        msg.answer_photo = AsyncMock(return_value=sent_photo("abc"))
        await screens.send(msg, "today", "first")
        await screens.send(msg, "today", "second")
        first, second = (c.args[0] for c in msg.answer_photo.await_args_list)
        self.assertEqual(first.path, screens.PICTURES_DIR / "today.jpeg")
        self.assertEqual(second, "abc")


class EditTest(unittest.IsolatedAsyncioTestCase):
    async def test_text_message_edits_text(self):
        msg = message()
        msg.edit_text = AsyncMock()
        await screens.edit(msg, "hi")
        self.assertEqual(msg.edit_text.await_args.args[0], "hi")

    async def test_photo_keeps_picture(self):
        msg = message()
        msg.photo = [MagicMock()]
        msg.edit_caption = AsyncMock()
        await screens.edit(msg, "hi")
        self.assertEqual(msg.edit_caption.await_args.kwargs["caption"], "hi")

    async def test_photo_swaps_picture(self):
        msg = message()
        msg.photo = [MagicMock()]
        msg.edit_media = AsyncMock()
        screens._file_ids.clear()
        await screens.edit(msg, "hi", picture="location")
        media = msg.edit_media.await_args.args[0]
        self.assertEqual((media.caption, media.media.path.stem), ("hi", "location"))


class PicturesTest(unittest.TestCase):
    def test_every_picture_exists(self):
        for picture in screens.PICTURES:
            self.assertTrue((screens.PICTURES_DIR / f"{picture}.jpeg").is_file(), picture)

    def test_real_menus_fit_in_a_caption(self):
        week = parse_week(FIXTURE)
        for lang in ("en", "nl"):
            for day in range(5):
                visible = unescape(re.sub(r"<[^>]+>", "", format_day(week, day, lang, "Geel")))
                self.assertLess(len(visible), CAPTION_LIMIT, (lang, day))


if __name__ == "__main__":
    unittest.main()
