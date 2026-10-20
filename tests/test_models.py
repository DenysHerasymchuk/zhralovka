import json
import unittest
from datetime import date
from pathlib import Path

from menu.models import DAYS, parse_week

FIXTURE = (Path(__file__).parent / "fixtures" / "geel.json").read_text()


def raw_week(**item_overrides) -> str:
    """A minimal API body, double-encoded like the real one."""
    item = {
        "ShortDescriptionEN": "  Leek soup  ",
        "ShortDescriptionNL": "Preisoep",
        "Category": {"NameEN": "Soup", "NameNL": "Soep"},
        "choiceGroups": [],
        **item_overrides,
    }
    week = [{
        "items": {"cat": {"Monday": item}},
        "startdate": "2026-10-12T00:00:00+00:00",
        "kitchen": {"Description": "Sanderus", "Campus": "Antwerpen"},
    }]
    return json.dumps(json.dumps(week))


class ParseWeekTest(unittest.TestCase):
    def test_real_response(self):
        week = parse_week(FIXTURE)
        self.assertEqual(week.start, date(2026, 10, 12))
        self.assertEqual(week.kitchen, "Geel")
        self.assertEqual(list(week.days), list(DAYS))
        monday = week.days["Monday"]
        self.assertEqual(monday[0].category_en, "Soup")
        self.assertEqual(monday[0].en, "🌿 Carrot soup 🌿")
        self.assertTrue(all(len(dishes) > 0 for dishes in week.days.values()))

    def test_empty_week_is_none(self):
        self.assertIsNone(parse_week('"[]"'))
        self.assertIsNone(parse_week("[]"))

    def test_trims_whitespace(self):
        dish = parse_week(raw_week()).days["Monday"][0]
        self.assertEqual(dish.en, "Leek soup")

    def test_skips_empty_dishes(self):
        week = parse_week(raw_week(ShortDescriptionEN=" ", ShortDescriptionNL=None))
        self.assertEqual(week.days["Monday"], [])

    def test_bad_json_raises(self):
        with self.assertRaises(ValueError):
            parse_week("<html>oops</html>")


if __name__ == "__main__":
    unittest.main()
