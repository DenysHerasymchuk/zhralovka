import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.exceptions import TelegramForbiddenError

import db
import notifier
from config import TIMEZONE
from menu.models import DAYS, Week
from tests.helpers import WEEK, HandlerTestCase


def at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 10, day, hour, minute, tzinfo=TIMEZONE)


class NextRunTest(unittest.TestCase):
    def test_later_today(self):
        self.assertEqual(notifier.next_run(at(13, 9)), at(13, 11))  # Tuesday morning

    def test_after_send_time_moves_to_tomorrow(self):
        self.assertEqual(notifier.next_run(at(13, 11)), at(14, 11))

    def test_friday_evening_skips_to_monday(self):
        self.assertEqual(notifier.next_run(at(16, 18)), at(19, 11))


class SendDailyTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.bot = MagicMock()
        self.bot.send_message = AsyncMock()
        patcher = patch("notifier.SEND_INTERVAL", 0)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def subscribe(self, user_id, campus, lang="en"):
        await db.add_user(user_id, lang)
        await db.set_campus(user_id, campus)
        await db.set_subscribed(user_id, True)

    async def test_sends_to_each_subscriber_fetching_each_campus_once(self):
        await self.subscribe(1, "Geel")
        await self.subscribe(2, "Geel", "nl")
        await self.subscribe(3, "Lier")
        fetch = AsyncMock(return_value=WEEK)
        with patch("notifier.fetch_week", fetch):
            sent = await notifier.send_daily(self.bot, 1)
        self.assertEqual(sent, 3)
        self.assertEqual(sorted(c.args[0] for c in fetch.await_args_list), ["Geel", "Lier"])
        dutch = next(c for c in self.bot.send_message.await_args_list if c.args[0] == 2)
        self.assertIn("<b>Dinsdag</b>", dutch.args[1])
        self.assertEqual([b.callback_data for b in dutch.kwargs["reply_markup"].inline_keyboard[0]], ["nav:0", "nav:2"])

    async def test_empty_day_sends_nothing(self):
        await self.subscribe(1, "Geel")
        empty = Week("Geel", WEEK.start, {day: [] for day in DAYS})
        with patch("notifier.fetch_week", AsyncMock(return_value=empty)):
            self.assertEqual(await notifier.send_daily(self.bot, 1), 0)
        self.bot.send_message.assert_not_awaited()

    async def test_blocked_user_is_unsubscribed(self):
        await self.subscribe(1, "Geel")
        self.bot.send_message.side_effect = TelegramForbiddenError(MagicMock(), "bot was blocked by the user")
        with patch("notifier.fetch_week", AsyncMock(return_value=WEEK)):
            self.assertEqual(await notifier.send_daily(self.bot, 1), 0)
        self.assertFalse(await db.is_subscribed(1))


if __name__ == "__main__":
    unittest.main()
