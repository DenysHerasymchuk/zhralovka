import string
import unittest

from i18n import TEXTS, all_langs, detect_lang


class I18nTest(unittest.TestCase):
    def test_detect_lang(self):
        self.assertEqual(detect_lang("nl"), "nl")
        self.assertEqual(detect_lang("nl-BE"), "nl")
        self.assertEqual(detect_lang("uk"), "en")
        self.assertEqual(detect_lang(None), "en")

    def test_languages_have_the_same_keys_and_placeholders(self):
        self.assertEqual(TEXTS["en"].keys(), TEXTS["nl"].keys())
        fields = lambda s: {f for _, f, _, _ in string.Formatter().parse(s) if f}
        for key in TEXTS["en"]:
            self.assertEqual(fields(TEXTS["en"][key]), fields(TEXTS["nl"][key]), key)

    def test_buttons_match_in_both_languages(self):
        self.assertEqual(all_langs("btn_today"), {"🍽 Today", "🍽 Vandaag"})


if __name__ == "__main__":
    unittest.main()
