from datetime import date, timedelta
from html import escape
from urllib.parse import urlencode

from i18n import day_name, month_name, t
from menu.models import DAYS, Week, is_lunch

# Matched against the English category name; first hit wins.
CATEGORY_EMOJI = (
    ("soup", "🥣"),
    ("salad", "🥗"),
    ("sandwich", "🥪"),
    ("snack", "🍟"),
    ("suggestion", "⭐"),
    ("pasta", "🍝"),
    ("lunch", "🍽"),
    ("veg", "🌱"),
)
DEFAULT_EMOJI = "🍴"
IMAGE_SEARCH_URL = "https://www.google.com/search?"


def category_emoji(category_en: str) -> str:
    name = category_en.lower()
    return next((emoji for key, emoji in CATEGORY_EMOJI if key in name), DEFAULT_EMOJI)


def pick_day(today: date) -> tuple[int, bool]:
    """Index into DAYS and whether it's the weekend; weekends fall back to Monday."""
    weekday = today.weekday()
    return (weekday, False) if weekday < 5 else (0, True)


def _pick(lang: str, en: str, nl: str) -> str:
    return (en if lang == "en" else nl) or en or nl


def _dish_card(dish, lang: str) -> str:
    category = _pick(lang, dish.category_en, dish.category_nl)
    name = _pick(lang, dish.en, dish.nl)
    photos = IMAGE_SEARCH_URL + urlencode({"tbm": "isch", "q": name})
    return (
        f"<blockquote>{category_emoji(dish.category_en)} <b>{escape(category)}</b>\n"
        f'<a href="{escape(photos)}">{escape(name)}</a></blockquote>'
    )


def format_day(week: Week, day: int, lang: str, campus: str) -> str:
    when = week.start + timedelta(days=day)
    place = campus if week.kitchen in ("", campus) else f"{campus}, {week.kitchen}"
    lines = [
        f"<b>{day_name(lang, day).capitalize()}</b>, {when.day} {month_name(lang, when.month)}",
        f"📍 {escape(place)}",
        "",
    ]

    dishes = week.days[DAYS[day]]
    if not dishes:
        lines.append(t(lang, "no_dishes", day=day_name(lang, day)))
        return "\n".join(lines)

    # Lunch first; sorted() is stable, so the rest keep the kitchen's order.
    lines += (_dish_card(dish, lang) for dish in sorted(dishes, key=lambda d: not is_lunch(d)))
    return "\n".join(lines)
