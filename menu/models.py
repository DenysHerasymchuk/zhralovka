import json
from datetime import date
from typing import NamedTuple

CAMPUSES = ("Antwerpen", "De Nayer", "Geel", "Lier", "Mechelen", "Turnhout", "Vorselaar")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


class Dish(NamedTuple):
    category_en: str
    category_nl: str
    en: str
    nl: str


class Week(NamedTuple):
    kitchen: str
    start: date
    days: dict[str, list[Dish]]


def is_lunch(dish: Dish) -> bool:
    return "lunch" in dish.category_en.lower()


def _clean(value) -> str:
    return (value or "").strip()


def parse_week(raw: str) -> Week | None:
    """Parse the API body, or return None when no menu is published.

    The API wraps its JSON in a JSON string, so it gets decoded twice.
    """
    data = json.loads(raw)
    if isinstance(data, str):
        data = json.loads(data)
    if not data:
        return None

    week = data[0]
    days: dict[str, list[Dish]] = {day: [] for day in DAYS}
    for per_day in week["items"].values():
        for day, item in per_day.items():
            en, nl = _clean(item.get("ShortDescriptionEN")), _clean(item.get("ShortDescriptionNL"))
            if day not in days or not (en or nl):
                continue
            category = item.get("Category") or {}
            days[day].append(
                Dish(_clean(category.get("NameEN")), _clean(category.get("NameNL")), en, nl)
            )

    return Week(
        kitchen=_clean((week.get("kitchen") or {}).get("Description")),
        start=date.fromisoformat(week["startdate"][:10]),
        days=days,
    )
