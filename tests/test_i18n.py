import string
import unittest

from i18n import LANG_NAMES, LANGS, TEXTS, all_langs, category_name, day_short, detect_lang


class I18nTest(unittest.TestCase):
    def test_detect_lang(self):
        self.assertEqual(detect_lang("nl"), "nl")
        self.assertEqual(detect_lang("nl-BE"), "nl")
        self.assertEqual(detect_lang("uk"), "uk")
        self.assertEqual(detect_lang("ru"), "en")
        self.assertEqual(detect_lang(None), "en")

    def test_languages_have_the_same_keys_and_placeholders(self):
        fields = lambda s: {f for _, f, _, _ in string.Formatter().parse(s) if f}
        for lang in LANGS:
            self.assertEqual(TEXTS[lang].keys(), TEXTS["en"].keys(), lang)
            for key in TEXTS["en"]:
                self.assertEqual(fields(TEXTS[lang][key]), fields(TEXTS["en"][key]), (lang, key))

    def test_every_language_has_a_picker_name(self):
        self.assertEqual(set(LANG_NAMES), set(LANGS))

    def test_buttons_match_in_every_language(self):
        self.assertEqual(all_langs("btn_today"), {"🍽 Today", "🍽 Vandaag", "🍽 Сьогодні"})

    def test_short_day_names(self):
        self.assertEqual([day_short("uk", d) for d in range(5)], ["Пн", "Вт", "Ср", "Чт", "Пт"])
        self.assertEqual(day_short("nl", 4), "Vr")

    def test_ukrainian_category_names(self):
        self.assertEqual(category_name("uk", "Lunch of the day"), "Обід дня")
        self.assertIsNone(category_name("uk", "Chef's special"))
        self.assertIsNone(category_name("en", "Soup"))


if __name__ == "__main__":
    unittest.main()
