import unittest
from unittest.mock import AsyncMock, patch

import aiohttp

import db
from handlers import menu
from menu import translate
from tests.helpers import TUESDAY, WEEK, HandlerTestCase, message, sent_text

# WEEK has "Leek soup" every day plus "<Day> pasta", so 6 distinct names.
NAMES = sorted({"Leek soup", *(f"{day} pasta" for day in WEEK.days)})


def ukrainian(texts, target):
    return [f"UA {text}" for text in texts]


class LocalizeTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        patcher = patch("menu.translate.DEEPL_API_KEY", "secret:fx")
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_other_languages_are_untouched(self):
        with patch("menu.translate._deepl", AsyncMock()) as deepl:
            self.assertIs(await translate.localize(WEEK, "en"), WEEK)
            self.assertIs(await translate.localize(WEEK, "nl"), WEEK)
        deepl.assert_not_awaited()

    async def test_no_key_means_english(self):
        with patch("menu.translate.DEEPL_API_KEY", ""), patch("menu.translate._deepl", AsyncMock()) as deepl:
            self.assertIs(await translate.localize(WEEK, "uk"), WEEK)
        deepl.assert_not_awaited()

    async def test_translates_every_name_in_one_request(self):
        with patch("menu.translate._deepl", AsyncMock(side_effect=ukrainian)) as deepl:
            week = await translate.localize(WEEK, "uk")
        deepl.assert_awaited_once_with(NAMES, "UK")
        self.assertEqual(week.days["Tuesday"][0].en, "UA Leek soup")
        self.assertEqual(week.days["Tuesday"][0].nl, "Preisoep")  # only the English field is replaced

    async def test_second_week_comes_from_the_cache(self):
        with patch("menu.translate._deepl", AsyncMock(side_effect=ukrainian)) as deepl:
            await translate.localize(WEEK, "uk")
            week = await translate.localize(WEEK, "uk")
        deepl.assert_awaited_once()
        self.assertEqual(week.days["Friday"][1].en, "UA Friday pasta")
        self.assertEqual(len(await db.get_translations(NAMES, "uk")), len(NAMES))

    async def test_deepl_failure_keeps_english_and_caches_nothing(self):
        error = aiohttp.ClientResponseError(None, (), status=456)
        with patch("menu.translate._deepl", AsyncMock(side_effect=error)):
            week = await translate.localize(WEEK, "uk")
        self.assertEqual(week.days["Monday"][0].en, "Leek soup")
        self.assertEqual(await db.get_translations(NAMES, "uk"), {})

    async def test_prewarm_translates_every_campus_once(self):
        with patch("menu.translate.fetch_week", AsyncMock(return_value=WEEK)) as fetch, \
             patch("menu.translate._deepl", AsyncMock(side_effect=ukrainian)) as deepl:
            await translate.prewarm()
            await translate.prewarm()  # the next hour: everything is cached
        self.assertEqual(fetch.await_count, 2 * len(translate.CAMPUSES))
        deepl.assert_awaited_once()  # same dishes everywhere, so one request in total

    async def test_prewarm_does_nothing_without_a_key(self):
        with patch("menu.translate.DEEPL_API_KEY", ""), \
             patch("menu.translate.fetch_week", AsyncMock()) as fetch:
            await translate.prewarm()
        fetch.assert_not_awaited()

    def test_free_and_pro_hosts(self):
        self.assertEqual(translate._deepl_url("abc:fx"), "https://api-free.deepl.com/v2/translate")
        self.assertEqual(translate._deepl_url("abc"), "https://api.deepl.com/v2/translate")

    async def test_ukrainian_user_sees_translated_dishes(self):
        await db.set_campus(42, "Geel")
        await db.set_lang(42, "uk")
        msg = message()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)), \
             patch("menu.translate._deepl", AsyncMock(side_effect=ukrainian)):
            await menu.show_today(msg)
        self.assertIn(">UA Tuesday pasta</a>", sent_text(msg))


if __name__ == "__main__":
    unittest.main()
