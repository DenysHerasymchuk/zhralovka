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

    async def test_subscribe_toggles(self):
        await db.set_campus(42, "Geel")
        msg = message()
        await settings.subscribe(msg)
        self.assertTrue(await db.is_subscribed(42))
        self.assertIn("every weekday at 11:00", sent_text(msg))
        await settings.subscribe(msg)
        self.assertFalse(await db.is_subscribed(42))
        self.assertEqual(sent_text(msg), TEXTS["en"]["unsubscribed"])

    async def test_subscribe_without_campus_asks_for_one(self):
        msg = message()
        await settings.subscribe(msg)
        self.assertFalse(await db.is_subscribed(42))
        self.assertEqual(sent_text(msg), TEXTS["en"]["pick_campus"])

    async def test_settings_button_toggles_and_redraws(self):
        await db.set_campus(42, "Geel")
        cb = callback("settings:subscribe")
        await settings.subscribe_from_settings(cb)
        self.assertTrue(await db.is_subscribed(42))
        edit = cb.message.edit_text.await_args.kwargs
        self.assertIn("Daily menu: <b>on</b>", edit["text"])
        self.assertEqual(edit["reply_markup"].inline_keyboard[2][0].text, TEXTS["en"]["btn_daily_off"])


if __name__ == "__main__":
    unittest.main()
