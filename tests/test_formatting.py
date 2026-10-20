import unittest
from datetime import date

from formatting import category_emoji, format_day, pick_day
from menu.models import DAYS, Dish, Week


def week(*dishes: Dish, kitchen="Sanderus") -> Week:
    days = {day: [] for day in DAYS}
    days["Tuesday"] = list(dishes)
    return Week(kitchen=kitchen, start=date(2026, 10, 12), days=days)


SOUP = Dish("Soup", "Soep", "Leek soup", "Preisoep")


class FormatDayTest(unittest.TestCase):
    def test_english(self):
        text = format_day(week(SOUP), 1, "en", "Antwerpen")
        self.assertEqual(
            text,
            "<b>Tuesday</b>, 13 October\n📍 Antwerpen, Sanderus\n\n"
            '<blockquote>🥣 <b>Soup</b>\n<a href="https://www.google.com/search?tbm=isch&amp;q=Leek+soup">Leek soup</a></blockquote>',
        )

    def test_dutch(self):
        text = format_day(week(SOUP), 1, "nl", "Antwerpen")
        self.assertIn("<b>Dinsdag</b>, 13 oktober", text)
        self.assertIn("<blockquote>🥣 <b>Soep</b>\n<a href=\"https://www.google.com/search?tbm=isch&amp;q=Preisoep\">Preisoep</a>", text)

    def test_kitchen_same_as_campus_is_not_repeated(self):
        text = format_day(week(SOUP, kitchen="Geel"), 1, "en", "Geel")
        self.assertIn("📍 Geel\n", text)

    def test_falls_back_to_other_language(self):
        dish = Dish("Lunch of the day", "", "Tikka masala", "")
        text = format_day(week(dish), 1, "nl", "Geel")
        self.assertIn("🍽 <b>Lunch of the day</b>\n<a href=\"https://www.google.com/search?tbm=isch&amp;q=Tikka+masala\">Tikka masala</a>", text)

    def test_each_category_gets_its_student_price(self):
        cases = {
            "Soup": "€1,25", "Lunch of the day": "€5,40", "Suggestion menu": "€5,40",
            "Salad": "€5,40", "Sandwich of today": "€5,45", "Snack": "€6,00",
        }
        for category, price in cases.items():
            text = format_day(week(Dish(category, "", "Dish", "")), 1, "en", "Geel", prices=True)
            self.assertIn(f"<b>{category}</b> · {price}\n", text)

    def test_prices_hidden_by_default(self):
        self.assertNotIn("€", format_day(week(SOUP), 1, "en", "Geel"))

    def test_unknown_category_has_no_price(self):
        text = format_day(week(Dish("Chef's special", "", "Dish", "")), 1, "en", "Geel", prices=True)
        self.assertIn("<b>Chef&#x27;s special</b>\n", text)

    def test_lunch_goes_first(self):
        lunch = Dish("Lunch of the day", "Lunch van de dag", "Poké Bowl", "Poké Bowl")
        salad = Dish("Salad", "Salade", "Salad bar", "Salad bar")
        text = format_day(week(SOUP, salad, lunch), 1, "en", "Geel")
        self.assertLess(text.index("Lunch of the day"), text.index("Soup"))
        self.assertLess(text.index("Soup"), text.index("Salad"))

    def test_escapes_html(self):
        dish = Dish("Snack", "Snack", "Fish & chips <3", "")
        text = format_day(week(dish), 1, "en", "Geel")
        self.assertIn("Fish &amp; chips &lt;3", text)

    def test_empty_day(self):
        text = format_day(week(SOUP), 0, "en", "Geel")
        self.assertIn("Nothing is listed for Monday", text)


class HelpersTest(unittest.TestCase):
    def test_category_emoji(self):
        self.assertEqual(category_emoji("Sandwich of today"), "🥪")
        self.assertEqual(category_emoji("Suggestion menu"), "⭐")
        self.assertEqual(category_emoji("Fusion revolution"), "🍴")

    def test_pick_day(self):
        tuesday, friday, saturday, sunday = (date(2026, 10, d) for d in (13, 16, 17, 18))
        self.assertEqual(pick_day(tuesday), (1, False))
        self.assertEqual(pick_day(friday), (4, False))
        self.assertEqual(pick_day(saturday), (0, True))
        self.assertEqual(pick_day(sunday), (0, True))


if __name__ == "__main__":
    unittest.main()
