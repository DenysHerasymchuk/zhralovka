import unittest
from unittest.mock import AsyncMock

import db
from handlers import notify
from i18n import TEXTS
from tests.helpers import HandlerTestCase, callback, message, sent_text


class ParseTimeTest(unittest.TestCase):
    def test_accepted_forms(self):
        for text, expected in (("10:45", "10:45"), ("9:05", "09:05"), ("10.45", "10:45"),
                               ("10h45", "10:45"), (" 07:00 ", "07:00"), ("23:59", "23:59")):
            self.assertEqual(notify.parse_time(text), expected, text)

    def test_rejected_forms(self):
        for text in ("24:00", "10:60", "1045", "abc", "10:5", "", "🍽 Today"):
            self.assertIsNone(notify.parse_time(text), text)


class NotifyHandlersTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await db.set_campus(42, "Geel")

    async def test_subscribe_toggles(self):
        msg = message()
        await notify.subscribe(msg)
        self.assertTrue((await db.get_notify(42))[0])
        self.assertIn("at 11:00", sent_text(msg))
        await notify.subscribe(msg)
        self.assertFalse((await db.get_notify(42))[0])
        self.assertEqual(sent_text(msg), TEXTS["en"]["unsubscribed"])

    async def test_subscribe_mentions_own_time(self):
        await db.set_notify_time(42, "09:15")
        msg = message()
        await notify.subscribe(msg)
        self.assertIn("at 09:15", sent_text(msg))

    async def test_subscribe_without_campus_asks_for_one(self):
        msg = message(user_id=7)
        await notify.subscribe(msg)
        self.assertFalse((await db.get_notify(7))[0])
        self.assertEqual(sent_text(msg), TEXTS["en"]["pick_campus"])

    async def test_settings_button_toggles_and_redraws(self):
        cb = callback("settings:subscribe")
        await notify.subscribe_from_settings(cb)
        self.assertTrue((await db.get_notify(42))[0])
        edit = cb.message.edit_text.await_args
        self.assertIn("Daily menu: <b>on · 11:00", edit.args[0])
        self.assertEqual(edit.kwargs["reply_markup"].inline_keyboard[3][0].text, TEXTS["en"]["btn_daily_off"])

    async def test_bad_time_gives_up_waiting(self):
        state = AsyncMock()
        reply = message("lunch?")
        await notify.save_time(reply, state)
        state.clear.assert_awaited_once()  # later messages are handled normally again
        self.assertEqual((await db.get_notify(42))[1], "11:00")
        self.assertEqual(sent_text(reply), TEXTS["en"]["bad_time"])

    async def test_change_time_flow(self):
        state = AsyncMock()
        cb = callback("settings:time")
        await notify.ask_time(cb, state)
        state.set_state.assert_awaited_once_with(notify.NotifyForm.time)
        self.assertEqual(cb.message.answer.await_args.args[0], TEXTS["en"]["ask_time"])

        reply = message("9.30")
        await notify.save_time(reply, state)
        state.clear.assert_awaited_once()
        self.assertEqual((await db.get_notify(42))[1], "09:30")
        self.assertEqual(sent_text(reply), "✅ <b>Daily menu at 09:30</b>")

    async def test_cancel_keeps_time(self):
        state = AsyncMock()
        await notify.cancel_time(message("/cancel"), state)
        state.clear.assert_awaited_once()
        self.assertEqual((await db.get_notify(42))[1], "11:00")

    async def test_toggle_days(self):
        cb = callback("ndays:2")
        await notify.toggle_day(cb)
        self.assertEqual((await db.get_notify(42))[2], "0134")
        row = cb.message.edit_text.await_args.kwargs["reply_markup"].inline_keyboard[0]
        self.assertEqual([b.text for b in row], ["✅ Mo", "✅ Tu", "We", "✅ Th", "✅ Fr"])

        await notify.toggle_day(callback("ndays:2"))
        self.assertEqual((await db.get_notify(42))[2], "01234")

    async def test_last_day_cannot_be_removed(self):
        await db.set_notify_days(42, "3")
        cb = callback("ndays:3")
        await notify.toggle_day(cb)
        self.assertEqual((await db.get_notify(42))[2], "3")
        self.assertTrue(cb.answer.await_args.kwargs["show_alert"])

    async def test_done_returns_to_settings(self):
        cb = callback("ndays:done")
        await notify.toggle_day(cb)
        self.assertIn("⚙️ <b>Settings</b>", cb.message.edit_text.await_args.args[0])

    async def test_bad_day_is_ignored(self):
        cb = callback("ndays:6")
        await notify.toggle_day(cb)
        cb.message.edit_text.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
