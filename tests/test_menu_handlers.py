import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import db
from handlers import menu
from i18n import TEXTS
from menu.client import MenuUnavailable
from tests.helpers import (
    SATURDAY,
    TUESDAY,
    WEEK,
    HandlerTestCase,
    callback,
    message,
    sent_markup,
    sent_picture,
    sent_text,
)


class MenuHandlersTest(HandlerTestCase):
    async def test_no_campus_asks_for_one(self):
        msg = message()
        await menu.show_today(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["pick_campus"])
        self.assertEqual(sent_picture(msg), "location")

    async def test_dutch_user_gets_dutch(self):
        msg = message(language_code="nl")
        await menu.show_today(msg)
        self.assertEqual(sent_text(msg), TEXTS["nl"]["pick_campus"])

    async def test_today_on_a_weekday(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
        self.assertIn("<b>Tuesday</b>, 13 October", sent_text(msg))
        self.assertEqual(sent_picture(msg), "today")

    async def test_today_with_last_weeks_menu_says_no_menu(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY + timedelta(days=7)), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
        self.assertIn("Geel hasn't published", sent_text(msg))

    async def test_today_on_weekend(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=SATURDAY):
            await menu.show_today(msg)
        self.assertIn("It's Saturday", sent_text(msg))

    async def test_week_opens_on_monday_at_the_weekend(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=SATURDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_week(msg)
        self.assertIn("<b>Monday</b>, 12 October", sent_text(msg))
        self.assertEqual(sent_picture(msg), "thisweek")
        self.assertEqual(sent_markup(msg).inline_keyboard[0][0].text, "🇺🇦")

    async def test_no_menu_published(self):
        await db.set_campus(42, "Lier")
        msg = message()
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=None)):
            await menu.show_week(msg)
        self.assertIn("Lier hasn't published", sent_text(msg))

    async def test_service_down(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(side_effect=MenuUnavailable)):
            await menu.show_today(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["unavailable"])

    async def test_switch_day_edits_message(self):
        await db.set_campus(42, "Geel")
        cb = callback("day:4")
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.switch_day(cb)
        self.assertIn("<b>Friday</b>, 16 October", cb.message.edit_text.await_args.args[0])

    async def test_today_day_nav_buttons(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
        row = sent_markup(msg).inline_keyboard[0]
        self.assertEqual([b.callback_data for b in row], ["nav:0", "nav:2"])

        cb = callback("nav:2")
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.switch_day(cb)
        edit = cb.message.edit_text.await_args
        self.assertIn("<b>Wednesday</b>", edit.args[0])
        self.assertEqual([b.callback_data for b in edit.kwargs["reply_markup"].inline_keyboard[0]], ["nav:1", "nav:3"])

    async def test_leaving_today_swaps_banner_to_this_week(self):
        await db.set_campus(42, "Geel")
        for target, banner in (("2", "thisweek"), ("1", "today")):  # Wednesday, then back to Tuesday
            cb = callback(f"nav:{target}")
            cb.message.photo = [MagicMock()]
            cb.message.edit_media = AsyncMock()
            with patch("handlers.menu.today", return_value=TUESDAY), \
                 patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
                await menu.switch_day(cb)
            self.assertEqual(cb.message.edit_media.await_args.args[0].media.path.stem, banner)

    async def test_monday_has_only_next_and_friday_only_previous(self):
        await db.set_campus(42, "Geel")
        for day, expected in (("0", ["nav:1"]), ("4", ["nav:3"])):
            cb = callback(f"nav:{day}")
            with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
                await menu.switch_day(cb)
            row = cb.message.edit_text.await_args.kwargs["reply_markup"].inline_keyboard[0]
            self.assertEqual([b.callback_data for b in row], expected)

    async def test_switch_day_alert_is_plain_text(self):
        await db.set_campus(42, "Geel")
        cb = callback("day:1")
        with patch("handlers.menu.fetch_week", AsyncMock(side_effect=MenuUnavailable)):
            await menu.switch_day(cb)
        alert = cb.answer.await_args.args[0]
        self.assertNotIn("<", alert)
        self.assertTrue(alert.startswith("⚠️ Menu unavailable"))

    async def test_week_view_day_switch_keeps_the_picture(self):
        await db.set_campus(42, "Geel")
        cb = callback("day:2")
        cb.message.photo = ["a photo"]
        cb.message.edit_caption = AsyncMock()
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.switch_day(cb)
        self.assertIn("<b>Wednesday</b>", cb.message.edit_caption.await_args.kwargs["caption"])
        cb.message.edit_text.assert_not_awaited()

    async def test_bad_day_is_ignored(self):
        await db.set_campus(42, "Geel")
        cb = callback("day:9")
        await menu.switch_day(cb)
        cb.message.edit_text.assert_not_awaited()

    async def test_garbage_callback_is_ignored(self):
        await db.set_campus(42, "Geel")
        cb = callback("day:x")
        await menu.switch_day(cb)
        cb.message.edit_text.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
