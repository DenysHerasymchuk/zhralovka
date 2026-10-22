from datetime import date, timedelta
from html import escape
from urllib.parse import urlencode

from i18n import category_name, day_name, month_name, t
from menu.models import DAYS, Week, is_lunch
from menu.prices import SECTIONS, UK_NAMES, category_price

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
    """The API only has English and Dutch, so every other language gets English."""
    return (nl if lang == "nl" else en) or en or nl


def _price_name(lang: str, en: str, nl: str) -> str:
    return UK_NAMES[en] if lang == "uk" else _pick(lang, en, nl)


def _dish_link(dish, lang: str) -> str:
    """The dish name, linked to a Google Images search for it."""
    name = _pick(lang, dish.en, dish.nl)
    photos = IMAGE_SEARCH_URL + urlencode({"tbm": "isch", "q": name})
    return f'<a href="{escape(photos)}">{escape(name)}</a>'


def _dish_card(dish, lang: str, prices: bool) -> str:
    category = category_name(lang, dish.category_en) or _pick(lang, dish.category_en, dish.category_nl)
    price = category_price(dish.category_en) if prices else None
    cost = f" · {_euro(price.student)}" if price else ""
    return (
        f"<blockquote>{category_emoji(dish.category_en)} <b>{escape(category)}</b>{cost}\n"
        f"{_dish_link(dish, lang)}</blockquote>"
    )


def _sorted_dishes(week: Week, day: int) -> list:
    # Lunch first, the rest in the kitchen's order.
    return sorted(week.days[DAYS[day]], key=lambda d: not is_lunch(d))


def _date_label(week: Week, day: int, lang: str) -> str:
    when = week.start + timedelta(days=day)
    return f"{when.day} {month_name(lang, when.month)}"


def _day_header(week: Week, day: int, lang: str, campus: str) -> list[str]:
    place = campus if week.kitchen in ("", campus) else f"{campus}, {week.kitchen}"
    return [
        f"<b>{day_name(lang, day).capitalize()}</b>, {_date_label(week, day, lang)}",
        f"📍 {escape(place)}",
        "",
    ]


def format_day(week: Week, day: int, lang: str, campus: str, prices: bool = False) -> str:
    lines = _day_header(week, day, lang, campus)
    dishes = _sorted_dishes(week, day)
    if not dishes:
        lines.append(t(lang, "no_dishes", day=day_name(lang, day)))
        return "\n".join(lines)

    lines += (_dish_card(dish, lang, prices) for dish in dishes)
    return "\n".join(lines)


def format_hot_meal(week: Week, day: int, lang: str, campus: str, prices: bool = False) -> str | None:
    """Like format_day, but with only the day's lunch; None if the kitchen lists none."""
    meals = [dish for dish in week.days[DAYS[day]] if is_lunch(dish)]
    if not meals:
        return None
    header = _day_header(week, day, lang, campus)[:2]  # no blank line: the card sits right under the campus
    return "\n".join(header + [_dish_card(dish, lang, prices) for dish in meals])


def _euro(cents: int) -> str:
    return f"€{cents // 100},{cents % 100:02}"


def _price_card(item, lang: str) -> str:
    prices = f"🎓 {_euro(item.student)} · 🏢 {_euro(item.intern)} · 💳 {_euro(item.bancontact)}"
    return f"<blockquote><b>{escape(_price_name(lang, item.en, item.nl))}</b>\n{prices}</blockquote>"


def format_prices(section: int, lang: str) -> str:
    current = SECTIONS[section]
    lines = [f"<b>{current.emoji} {escape(_price_name(lang, current.en, current.nl))}</b>", ""]
    lines += (_price_card(item, lang) for item in current.items)
    return "\n".join(lines)
