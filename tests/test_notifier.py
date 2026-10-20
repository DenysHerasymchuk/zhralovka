import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.exceptions import TelegramForbiddenError

import db
import notifier
from menu.models import DAYS, Week
from tests.helpers import TUESDAY, WEEK, HandlerTestCase


class SendDueTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.bot = MagicMock()
        self.bot.send_photo = AsyncMock()
        patcher = patch("notifier.SEND_INTERVAL", 0)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def subscribe(self, user_id, campus, lang="en", hhmm="11:00", days="01234"):
        await db.add_user(user_id, lang)
        await db.set_campus(user_id, campus)
        await db.set_subscribed(user_id, True)
        await db.set_notify_time(user_id, hhmm)
        await db.set_notify_days(user_id, days)

    async def test_sends_to_each_subscriber_fetching_each_campus_once(self):
        await self.subscribe(1, "Geel")
        await self.subscribe(2, "Geel", "nl")
        await self.subscribe(3, "Lier")
        fetch = AsyncMock(return_value=WEEK)
        with patch("notifier.fetch_week", fetch):
            sent = await notifier.send_due(self.bot, TUESDAY,"11:00")
        self.assertEqual(sent, 3)
        self.assertEqual(sorted(c.args[0] for c in fetch.await_args_list), ["Geel", "Lier"])
        dutch = next(c for c in self.bot.send_photo.await_args_list if c.args[0] == 2)
        self.assertIn("<b>Dinsdag</b>", dutch.kwargs["caption"])
        self.assertEqual(dutch.args[1].path.stem, "daily")
        self.assertEqual([b.callback_data for b in dutch.kwargs["reply_markup"].inline_keyboard[0]], ["nav:0", "nav:2"])
        self.assertNotIn("€", dutch.kwargs["caption"])

    async def test_only_users_due_this_minute_and_day(self):
        await self.subscribe(1, "Geel", hhmm="09:30")
        await self.subscribe(2, "Geel", hhmm="11:00")
        await self.subscribe(3, "Geel", hhmm="09:30", days="024")
        fetch = AsyncMock(return_value=WEEK)
        with patch("notifier.fetch_week", fetch):
            self.assertEqual(await notifier.send_due(self.bot, TUESDAY,"09:30"), 1)
        self.assertEqual(self.bot.send_photo.await_args.args[0], 1)

    async def test_nobody_due_skips_fetching(self):
        await self.subscribe(1, "Geel")
        fetch = AsyncMock(return_value=WEEK)
        with patch("notifier.fetch_week", fetch):
            self.assertEqual(await notifier.send_due(self.bot, TUESDAY,"08:00"), 0)
        fetch.assert_not_awaited()

    async def test_empty_day_sends_nothing(self):
        await self.subscribe(1, "Geel")
        empty = Week("Geel", WEEK.start, {day: [] for day in DAYS})
        with patch("notifier.fetch_week", AsyncMock(return_value=empty)):
            self.assertEqual(await notifier.send_due(self.bot, TUESDAY,"11:00"), 0)
        self.bot.send_photo.assert_not_awaited()

    async def test_last_weeks_menu_is_not_sent(self):
        await self.subscribe(1, "Geel")
        with patch("notifier.fetch_week", AsyncMock(return_value=WEEK)):
            self.assertEqual(await notifier.send_due(self.bot, TUESDAY + timedelta(days=7), "11:00"), 0)
        self.bot.send_photo.assert_not_awaited()

    async def test_blocked_user_is_unsubscribed(self):
        await self.subscribe(1, "Geel")
        self.bot.send_photo.side_effect = TelegramForbiddenError(MagicMock(), "bot was blocked by the user")
        with patch("notifier.fetch_week", AsyncMock(return_value=WEEK)):
            self.assertEqual(await notifier.send_due(self.bot, TUESDAY,"11:00"), 0)
        self.assertFalse((await db.get_notify(1))[0])


if __name__ == "__main__":
    unittest.main()
