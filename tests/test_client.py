import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch

import aiohttp

from config import TIMEZONE
from menu import client
from tests.test_models import raw_week


def at(*parts) -> float:
    return datetime(*parts, tzinfo=TIMEZONE).timestamp()


class FetchWeekTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        client._cache.clear()

    async def test_url_encodes_campus_and_caches(self):
        with patch("menu.client._get", AsyncMock(return_value=raw_week())) as get:
            first = await client.fetch_week("De Nayer")
            second = await client.fetch_week("De Nayer")
        get.assert_awaited_once_with(client.API_URL + "De%20Nayer")
        self.assertIs(first, second)

    async def test_empty_week_is_cached_as_none(self):
        with patch("menu.client._get", AsyncMock(return_value='"[]"')) as get:
            self.assertIsNone(await client.fetch_week("Lier"))
            self.assertIsNone(await client.fetch_week("Lier"))
        get.assert_awaited_once()

    async def test_network_error_becomes_menu_unavailable(self):
        with patch("menu.client._get", AsyncMock(side_effect=aiohttp.ClientError())):
            with self.assertRaises(client.MenuUnavailable):
                await client.fetch_week("Geel")
        self.assertNotIn("Geel", client._cache)

    async def test_current_week_is_kept_until_next_monday_morning(self):
        tuesday = at(2026, 10, 13, 12)  # raw_week() starts Monday 12 October
        with patch("menu.client._get", AsyncMock(return_value=raw_week())) as get:
            with patch("menu.client.time.time", return_value=tuesday):
                await client.fetch_week("Geel")
            for moment in (at(2026, 10, 16, 18), at(2026, 10, 19, 6, 59)):  # Friday evening, Monday 06:59
                with patch("menu.client.time.time", return_value=moment):
                    await client.fetch_week("Geel")
            self.assertEqual(get.await_count, 1)
            with patch("menu.client.time.time", return_value=at(2026, 10, 19, 7, 1)):
                await client.fetch_week("Geel")
        self.assertEqual(get.await_count, 2)

    async def test_last_weeks_menu_is_retried_after_half_an_hour(self):
        monday_early = at(2026, 10, 19, 7, 0)  # the kitchen still serves week 12 October
        with patch("menu.client._get", AsyncMock(return_value=raw_week())) as get:
            with patch("menu.client.time.time", return_value=monday_early):
                await client.fetch_week("Geel")
            with patch("menu.client.time.time", return_value=monday_early + 29 * 60):
                await client.fetch_week("Geel")
            self.assertEqual(get.await_count, 1)
            with patch("menu.client.time.time", return_value=monday_early + 31 * 60):
                await client.fetch_week("Geel")
        self.assertEqual(get.await_count, 2)

    async def test_no_menu_is_retried_after_half_an_hour(self):
        self.assertEqual(client._valid_until(None, 1000.0), 1000.0 + client.RETRY_AFTER)

    async def test_garbage_body_becomes_menu_unavailable(self):
        with patch("menu.client._get", AsyncMock(return_value='"{\\"nope\\": 1}"')):
            with self.assertRaises(client.MenuUnavailable):
                await client.fetch_week("Geel")


if __name__ == "__main__":
    unittest.main()
