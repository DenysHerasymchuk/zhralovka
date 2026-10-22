import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import db
from handlers import menu
from i18n import TEXTS
from menu.client import MenuUnavailable
from tests.helpers import (
    GROUP,
    SATURDAY,
    TUESDAY,
    WEEK,
    HandlerTestCase,
    callback,
    group_callback,
    group_message,
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

    async def test_week_buttons_in_ukrainian(self):
        await db.set_campus(42, "Geel")
        await db.set_lang(42, "uk")
        msg = message()
        with patch("handlers.menu.today", return_value=SATURDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_week(msg)
        labels = [b.text for b in sent_markup(msg).inline_keyboard[0]]
        self.assertEqual(labels, ["🇺🇦", "Вт 13", "Ср 14", "Чт 15", "Пт 16"])

    async def test_prices_follow_the_setting(self):
        await db.set_campus(42, "Geel")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
            self.assertNotIn("€", sent_text(msg))
            self.assertEqual(len(sent_markup(msg).inline_keyboard), 1)  # no toggle under the menu

            await db.set_show_prices(42, True)
            await menu.show_week(msg)
            self.assertIn("<b>Lunch of the day</b> · €5,40", sent_text(msg))

            cb = callback("nav:2")
            await menu.switch_day(cb)
        self.assertIn("· €5,40", cb.message.edit_text.await_args.args[0])

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


class SharedChatTest(HandlerTestCase):
    """A menu posted in a group belongs to the group, whoever taps its buttons."""

    GROUP = -100123

    async def test_tap_by_another_member_keeps_the_groups_campus(self):
        await db.set_campus(self.GROUP, "Geel")
        await db.set_campus(7, "Lier")  # the tapper's own DM campus
        cb = callback("day:2", user_id=7, chat_id=self.GROUP, chat_type="supergroup")
        fetch = AsyncMock(return_value=WEEK)
        with patch("handlers.menu.fetch_week", fetch):
            await menu.switch_day(cb)
        self.assertEqual(fetch.await_args.args[0], "Geel")

    async def test_tap_does_not_register_the_tapper(self):
        await db.set_campus(self.GROUP, "Geel")
        cb = callback("day:2", user_id=7, chat_id=self.GROUP, chat_type="supergroup")
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.switch_day(cb)
        self.assertIsNone(await db.get_user(7))

    async def test_dm_still_uses_the_users_own_campus(self):
        await db.set_campus(42, "Lier")
        msg = message()
        fetch = AsyncMock(return_value=WEEK)
        with patch("handlers.menu.today", return_value=TUESDAY), patch("handlers.menu.fetch_week", fetch):
            await menu.show_today(msg)
        self.assertEqual(fetch.await_args.args[0], "Lier")


class HotMealTest(HandlerTestCase):
    async def shortm(self, msg, when=TUESDAY, week=WEEK):
        msg.reply = AsyncMock()
        with patch("handlers.menu.today", return_value=when), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=week)):
            await menu.show_hot_meal(msg)
        return msg.reply.await_args

    async def test_replies_with_the_date_campus_and_lunch_only(self):
        await db.set_campus(42, "Geel")
        msg = message("/shortm")
        call = await self.shortm(msg)
        text = call.args[0]
        self.assertTrue(text.startswith("<b>Tuesday</b>, 13 October\n📍 Geel\n"))
        self.assertIn("🍽 <b>Lunch of the day</b>", text)
        self.assertIn(">Tuesday pasta</a>", text)
        self.assertIn('href="https://www.google.com/search?tbm=isch&amp;q=Tuesday+pasta"', text)
        self.assertNotIn("soup", text.lower())
        self.assertTrue(call.kwargs["link_preview_options"].is_disabled)
        self.assertEqual([b.callback_data for b in call.kwargs["reply_markup"].inline_keyboard[0]], ["hot:0", "hot:2"])
        msg.answer_photo.assert_not_awaited()

    async def test_works_in_a_group_for_any_member(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/shortm")
        call = await self.shortm(msg)
        self.assertIn(">Tuesday pasta</a>", call.args[0])
        msg.bot.get_chat_member.assert_not_awaited()

    async def test_weekend(self):
        await db.set_campus(42, "Geel")
        call = await self.shortm(message("/shortm"), when=SATURDAY)
        self.assertIn("It's Saturday", call.args[0])

    async def test_last_weeks_menu_says_no_menu(self):
        await db.set_campus(42, "Geel")
        call = await self.shortm(message("/shortm"), when=TUESDAY + timedelta(days=7))
        self.assertIn("Geel hasn't published", call.args[0])

    async def test_shows_the_price_when_turned_on(self):
        await db.set_campus(42, "Geel")
        await db.set_show_prices(42, True)
        call = await self.shortm(message("/shortm"))
        self.assertIn("Lunch of the day</b> · €5,40", call.args[0])

    async def test_day_without_a_lunch(self):
        await db.set_campus(42, "Geel")
        soup_only = WEEK._replace(days={**WEEK.days, "Tuesday": WEEK.days["Tuesday"][:1]})
        call = await self.shortm(message("/shortm"), week=soup_only)
        self.assertTrue(call.args[0].endswith("📍 Geel\n" + TEXTS["en"]["no_hot_meal"]))

    async def test_no_campus_asks_for_one(self):
        msg = message("/shortm")
        msg.reply = AsyncMock()
        await menu.show_hot_meal(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["pick_campus"])


class HotMealNavigationTest(HandlerTestCase):
    async def tap(self, data, cb=None, week=WEEK):
        cb = cb or callback(data)
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=week)):
            await menu.switch_hot_meal(cb)
        return cb

    async def test_layout_has_no_blank_line_before_the_lunch(self):
        await db.set_campus(42, "Geel")
        cb = await self.tap("hot:2")
        text = cb.message.edit_text.await_args.args[0]
        self.assertIn("📍 Geel\n<blockquote>🍽 <b>Lunch of the day</b>", text)

    async def test_next_day_edits_the_same_message_with_that_days_lunch(self):
        await db.set_campus(42, "Geel")
        cb = await self.tap("hot:2")
        edit = cb.message.edit_text.await_args
        self.assertTrue(edit.args[0].startswith("<b>Wednesday</b>, 14 October"))
        self.assertIn(">Wednesday pasta</a>", edit.args[0])
        self.assertNotIn("soup", edit.args[0].lower())
        self.assertTrue(edit.kwargs["link_preview_options"].is_disabled)
        self.assertEqual([b.callback_data for b in edit.kwargs["reply_markup"].inline_keyboard[0]], ["hot:1", "hot:3"])
        cb.message.answer_photo.assert_not_awaited()

    async def test_edges_have_one_button(self):
        await db.set_campus(42, "Geel")
        monday = (await self.tap("hot:0")).message.edit_text.await_args.kwargs["reply_markup"]
        friday = (await self.tap("hot:4")).message.edit_text.await_args.kwargs["reply_markup"]
        self.assertEqual([b.callback_data for b in monday.inline_keyboard[0]], ["hot:1"])
        self.assertEqual([b.callback_data for b in friday.inline_keyboard[0]], ["hot:3"])

    async def test_group_buttons_use_the_groups_campus(self):
        await db.set_campus(GROUP, "Geel")
        await db.set_campus(7, "Lier")
        fetch = AsyncMock(return_value=WEEK)
        cb = group_callback("hot:3")
        with patch("handlers.menu.fetch_week", fetch):
            await menu.switch_hot_meal(cb)
        self.assertEqual(fetch.await_args.args[0], "Geel")

    async def test_bad_day_is_ignored(self):
        await db.set_campus(42, "Geel")
        cb = await self.tap("hot:9")
        cb.message.edit_text.assert_not_awaited()

    async def test_menu_service_down_shows_a_popup(self):
        await db.set_campus(42, "Geel")
        cb = callback("hot:2")
        with patch("handlers.menu.fetch_week", AsyncMock(side_effect=MenuUnavailable)):
            await menu.switch_hot_meal(cb)
        self.assertTrue(cb.answer.await_args.kwargs["show_alert"])
        cb.message.edit_text.assert_not_awaited()
