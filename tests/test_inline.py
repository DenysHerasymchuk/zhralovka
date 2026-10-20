import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import db
from handlers import inline
from menu.client import MenuUnavailable
from tests.helpers import SATURDAY, TUESDAY, WEEK, HandlerTestCase, message


def inline_query(query=""):
    q = MagicMock()
    q.query = query
    q.from_user = message().from_user
    q.answer = AsyncMock()
    return q


class InlineTest(HandlerTestCase):
    async def answer(self, query="", today=TUESDAY, week=WEEK):
        q = inline_query(query)
        fetch = AsyncMock(side_effect=week) if isinstance(week, type) else AsyncMock(return_value=week)
        with patch("handlers.inline.today", return_value=today), \
             patch("handlers.menu.fetch_week", fetch) as fetch:
            await inline.inline_menu(q)
        self.fetch = fetch
        return q.answer.await_args

    async def test_shows_today_to_friday_for_saved_campus(self):
        await db.set_campus(42, "Geel")
        results = (await self.answer()).args[0]
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].title, "Tuesday, 13 October · Geel")
        self.assertEqual(results[0].description, "Tuesday pasta · Leek soup")
        self.assertIn("<b>Tuesday</b>", results[0].input_message_content.message_text)

    async def test_weekend_shows_whole_week(self):
        await db.set_campus(42, "Geel")
        self.assertEqual(len((await self.answer(today=SATURDAY)).args[0]), 5)

    async def test_query_picks_another_campus(self):
        await db.set_campus(42, "Geel")
        results = (await self.answer("de na")).args[0]
        self.fetch.assert_awaited_once_with("De Nayer")
        self.assertTrue(results[0].title.endswith("· De Nayer"))

    async def test_no_campus_offers_to_pick_one(self):
        answer = await self.answer()
        self.assertEqual(answer.args[0], [])
        self.assertEqual(answer.kwargs["button"].start_parameter, "campus")

    async def test_stranger_is_not_registered(self):
        await self.answer("geel")
        self.assertIsNone(await db.get_user(42))

    async def test_service_down_returns_nothing(self):
        await db.set_campus(42, "Geel")
        self.assertEqual((await self.answer(week=MenuUnavailable)).args[0], [])


if __name__ == "__main__":
    unittest.main()
