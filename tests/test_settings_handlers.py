import unittest
from pathlib import Path
from unittest.mock import AsyncMock

import db
from handlers import settings
from i18n import TEXTS
from tests.helpers import HandlerTestCase, callback, message, sent_markup, sent_picture, sent_text


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
        msg.answer_photo.assert_not_awaited()
        await settings.switch_lang(msg)
        self.assertEqual((await db.get_user(42))[1], "en")

    async def test_language_button_edits_settings_in_place(self):
        await db.set_campus(42, "Geel")
        cb = callback("settings:lang")
        await settings.switch_lang_from_settings(cb)
        self.assertEqual((await db.get_user(42))[1], "nl")
        cb.message.delete.assert_not_awaited()
        cb.message.answer.assert_not_awaited()
        edit = cb.message.edit_text.await_args
        self.assertIn("⚙️ <b>Instellingen</b>", edit.args[0])
        self.assertEqual(edit.kwargs["reply_markup"].inline_keyboard[1][0].text, TEXTS["nl"]["btn_change_lang"])

    async def test_prices_button_toggles_and_redraws(self):
        cb = callback("settings:prices")
        await settings.toggle_prices(cb)
        self.assertTrue(await db.get_show_prices(42))
        edit = cb.message.edit_text.await_args
        self.assertIn("Prices in menus: <b>on</b>", edit.args[0])
        self.assertEqual(edit.kwargs["reply_markup"].inline_keyboard[2][0].text, TEXTS["en"]["btn_hide_prices"])
        await settings.toggle_prices(callback("settings:prices"))
        self.assertFalse(await db.get_show_prices(42))

    async def test_changing_campus_returns_to_settings(self):
        await db.set_campus(42, "Geel")
        cb = callback("campus:Lier")
        await settings.save_campus(cb)
        self.assertEqual((await db.get_user(42))[0], "Lier")
        cb.message.answer.assert_not_awaited()
        self.assertIn("Campus: <b>Lier</b>", cb.message.edit_text.await_args.args[0])

    async def test_first_campus_sends_bottom_keyboard(self):
        cb = callback("campus:Geel")
        await settings.save_campus(cb)
        self.assertEqual(sent_text(cb.message), TEXTS["en"]["campus_saved"].format(campus="Geel"))
        self.assertEqual(sent_markup(cb.message).keyboard[0][0].text, TEXTS["en"]["btn_today"])

    async def test_settings_show_daily_menu_details(self):
        await db.set_campus(42, "Geel")
        await db.set_subscribed(42, True)
        await db.set_notify_time(42, "10:45")
        await db.set_notify_days(42, "024")
        msg = message()
        await settings.show_settings(msg)
        self.assertEqual(sent_picture(msg), "settings")
        self.assertIn("Daily menu: <b>on · 10:45 · Mo, We, Fr</b>", sent_text(msg))
        rows = sent_markup(msg).inline_keyboard
        self.assertEqual([b.callback_data for b in rows[4]], ["settings:time", "settings:days"])

    async def test_settings_hide_time_and_days_when_off(self):
        msg = message()
        await settings.show_settings(msg)
        self.assertIn("Daily menu: <b>off</b>", sent_text(msg))
        self.assertEqual(len(sent_markup(msg).inline_keyboard), 4)

    async def test_change_campus_from_settings_swaps_the_picture(self):
        cb = callback("settings:campus")
        cb.message.photo = ["settings photo"]
        cb.message.edit_media = AsyncMock()
        await settings.ask_campus_from_settings(cb)
        media = cb.message.edit_media.await_args.args[0]
        self.assertEqual(Path(media.media.path).stem, "location")
        self.assertEqual(media.caption, TEXTS["en"]["pick_campus"])


if __name__ == "__main__":
    unittest.main()
