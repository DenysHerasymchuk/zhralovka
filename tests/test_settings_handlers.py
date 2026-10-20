import unittest

import db
from handlers import settings
from i18n import TEXTS
from tests.helpers import HandlerTestCase, callback, message, sent_text


class SettingsHandlersTest(HandlerTestCase):
    async def test_pick_campus_saves_it(self):
        cb = callback("campus:De Nayer")
        await settings.save_campus(cb)
        self.assertEqual((await db.get_user(42))[0], "De Nayer")

    async def test_unknown_campus_is_rejected(self):
        cb = callback("campus:Atlantis")
        await settings.save_campus(cb)
        self.assertIsNone(await db.get_user(42))

    async def test_language_toggle(self):
        msg = message()
        await settings.switch_lang(msg)
        self.assertEqual((await db.get_user(42))[1], "nl")
        self.assertEqual(sent_text(msg), TEXTS["nl"]["lang_saved"])
        await settings.switch_lang(msg)
        self.assertEqual((await db.get_user(42))[1], "en")


if __name__ == "__main__":
    unittest.main()
