import unittest
from unittest.mock import AsyncMock, patch

import aiohttp

from menu import client
from tests.test_models import raw_week


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

    async def test_garbage_body_becomes_menu_unavailable(self):
        with patch("menu.client._get", AsyncMock(return_value='"{\\"nope\\": 1}"')):
            with self.assertRaises(client.MenuUnavailable):
                await client.fetch_week("Geel")


if __name__ == "__main__":
    unittest.main()
