from datetime import date, timedelta
from html import escape
from urllib.parse import urlencode

from i18n import day_name, month_name, t
from menu.models import DAYS, Week, is_lunch
from menu.prices import SECTIONS, category_price

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


def _dish_card(dish, lang: str, prices: bool) -> str:
    category = _pick(lang, dish.category_en, dish.category_nl)
    name = _pick(lang, dish.en, dish.nl)
    photos = IMAGE_SEARCH_URL + urlencode({"tbm": "isch", "q": name})
    price = category_price(dish.category_en) if prices else None
    cost = f" · {_euro(price.student)}" if price else ""
    return (
        f"<blockquote>{category_emoji(dish.category_en)} <b>{escape(category)}</b>{cost}\n"
        f'<a href="{escape(photos)}">{escape(name)}</a></blockquote>'
    )


def _sorted_dishes(week: Week, day: int) -> list:
    # Lunch first, the rest in the kitchen's order.
    return sorted(week.days[DAYS[day]], key=lambda d: not is_lunch(d))


def _date_label(week: Week, day: int, lang: str) -> str:
    when = week.start + timedelta(days=day)
    return f"{when.day} {month_name(lang, when.month)}"


def day_title(week: Week, day: int, lang: str) -> str:
    return f"{day_name(lang, day).capitalize()}, {_date_label(week, day, lang)}"


def day_summary(week: Week, day: int, lang: str) -> str:
    return " · ".join(_pick(lang, d.en, d.nl) for d in _sorted_dishes(week, day))


def format_day(week: Week, day: int, lang: str, campus: str, prices: bool = False) -> str:
    place = campus if week.kitchen in ("", campus) else f"{campus}, {week.kitchen}"
    lines = [
        f"<b>{day_name(lang, day).capitalize()}</b>, {_date_label(week, day, lang)}",
        f"📍 {escape(place)}",
        "",
    ]

    dishes = _sorted_dishes(week, day)
    if not dishes:
        lines.append(t(lang, "no_dishes", day=day_name(lang, day)))
        return "\n".join(lines)

    lines += (_dish_card(dish, lang, prices) for dish in dishes)
    return "\n".join(lines)


def _euro(cents: int) -> str:
    return f"€{cents // 100},{cents % 100:02}"


def _price_card(item, lang: str) -> str:
    prices = f"🎓 {_euro(item.student)} · 🏢 {_euro(item.intern)} · 💳 {_euro(item.bancontact)}"
    return f"<blockquote><b>{escape(_pick(lang, item.en, item.nl))}</b>\n{prices}</blockquote>"


def format_prices(section: int, lang: str) -> str:
    current = SECTIONS[section]
    lines = [f"<b>{current.emoji} {escape(_pick(lang, current.en, current.nl))}</b>", ""]
    lines += (_price_card(item, lang) for item in current.items)
    return "\n".join(lines)
