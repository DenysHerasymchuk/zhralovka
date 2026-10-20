import re
import unittest

from formatting import format_prices
from handlers import prices
from menu.prices import SECTIONS, UK_NAMES
from tests.helpers import HandlerTestCase, callback, message, sent_markup, sent_picture, sent_text


class PriceDataTest(unittest.TestCase):
    def test_every_item_is_complete(self):
        for section in SECTIONS:
            for item in section.items:
                self.assertTrue(item.nl and item.en, item)
                self.assertTrue(all(cents > 0 for cents in item[2:]), item)
                self.assertLessEqual(item.student, item.bancontact, item)

    def test_every_name_has_a_ukrainian_translation(self):
        for section in SECTIONS:
            self.assertIn(section.en, UK_NAMES)
            for item in section.items:
                self.assertIn(item.en, UK_NAMES)

    def test_ukrainian_board(self):
        text = format_prices(1, "uk")
        self.assertIn("<b>🍲 Гарячі страви</b>", text)
        self.assertIn("<b>Страва дня</b>\n🎓 €5,40", text)

    def test_every_section_fits_a_photo_caption(self):
        for lang in ("en", "nl", "uk"):
            for i in range(len(SECTIONS)):
                visible = re.sub(r"<[^>]+>", "", format_prices(i, lang))
                self.assertLess(len(visible), 1024, (lang, i))


class FormatPricesTest(unittest.TestCase):
    def test_sandwiches_in_english(self):
        text = format_prices(0, "en")
        self.assertTrue(text.startswith("<b>🥪 Sandwiches</b>\n\n<blockquote>"))
        self.assertIn("<blockquote><b>Bread roll</b>\n🎓 €0,95 · 🏢 €0,95 · 💳 €1,20</blockquote>", text)
        self.assertNotIn("<pre>", text)

    def test_dutch_names(self):
        text = format_prices(1, "nl")
        self.assertIn("<b>🍲 Warm eten</b>", text)
        self.assertIn("<b>Dagschotel</b>\n🎓 €5,40 · 🏢 €10,10 · 💳 €12,20", text)

    def test_names_are_escaped(self):
        self.assertIn("<b>Friet + saus</b>", format_prices(1, "nl"))
        self.assertNotIn("&lt;", format_prices(4, "en"))


class PricesHandlerTest(HandlerTestCase):
    async def test_menu_opens_sandwiches(self):
        msg = message()
        await prices.show_prices(msg)
        self.assertIn("<b>🥪 Sandwiches</b>", sent_text(msg))
        self.assertEqual(sent_picture(msg), "menu")
        buttons = sent_markup(msg).inline_keyboard[0]
        self.assertEqual(len(buttons), len(SECTIONS))
        self.assertEqual(buttons[0].text, "✅ 🥪")

    async def test_section_button_switches(self):
        cb = callback("prices:3")
        await prices.switch_section(cb)
        edit = cb.message.edit_text.await_args
        self.assertIn("<b>🍰 Desserts</b>", edit.args[0])
        self.assertEqual(edit.kwargs["reply_markup"].inline_keyboard[0][3].text, "✅ 🍰")

    async def test_bad_section_is_ignored(self):
        for data in ("prices:9", "prices:x", "prices:²", "prices:-1"):
            cb = callback(data)
            await prices.switch_section(cb)
            cb.message.edit_text.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
