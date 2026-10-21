import unittest

from aiogram.types import ReplyKeyboardRemove

import db
from handlers import clear
from i18n import TEXTS
from tests.helpers import GROUP, HandlerTestCase, group_message, message, sent_markup, sent_text


class ClearTest(HandlerTestCase):
    async def test_dm_removes_the_keyboard(self):
        msg = message("/clear")
        await clear.clear(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["menu_cleared"])
        self.assertIsInstance(sent_markup(msg), ReplyKeyboardRemove)

    async def test_dm_keeps_the_users_settings(self):
        await db.set_campus(42, "Geel")
        await clear.clear(message("/clear"))
        self.assertEqual(await db.get_user(42), ("Geel", "en"))

    async def test_admin_clears_a_group(self):
        msg = group_message("/clear", admin=True)
        await clear.clear(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["menu_cleared_group"])
        self.assertIsInstance(sent_markup(msg), ReplyKeyboardRemove)

    async def test_member_cannot_clear_a_group(self):
        msg = group_message("/clear")
        await clear.clear(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["admins_only"])
        self.assertNotIn("reply_markup", msg.answer.await_args.kwargs)

    async def test_follows_the_chats_language(self):
        await db.add_user(GROUP, "uk")
        msg = group_message("/clear", admin=True)
        await clear.clear(msg)
        self.assertEqual(sent_text(msg), TEXTS["uk"]["menu_cleared_group"])


if __name__ == "__main__":
    unittest.main()
