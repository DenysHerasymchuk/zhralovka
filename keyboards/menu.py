from datetime import date, timedelta

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from i18n import day_name, t
from menu.models import CAMPUSES


def main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_today")), KeyboardButton(text=t(lang, "btn_week"))],
            [KeyboardButton(text=t(lang, "btn_settings"))],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=t(lang, "placeholder"),
    )


def campus_keyboard(current: str | None = None) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"📍 {campus}" if campus == current else campus,
            callback_data=f"campus:{campus}",
        )
        for campus in CAMPUSES
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])


def days_keyboard(start: date, selected: int, lang: str) -> InlineKeyboardMarkup:
    buttons = []
    for day in range(5):
        label = f"{day_name(lang, day)[:2].capitalize()} {(start + timedelta(days=day)).day}"
        buttons.append(
            InlineKeyboardButton(
                text="🇺🇦" if day == selected else label,
                callback_data=f"day:{day}",
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def day_nav_keyboard(day: int, lang: str) -> InlineKeyboardMarkup | None:
    buttons = []
    if day > 0:
        buttons.append(InlineKeyboardButton(text=t(lang, "btn_prev_day"), callback_data=f"nav:{day - 1}"))
    if day < 4:
        buttons.append(InlineKeyboardButton(text=t(lang, "btn_next_day"), callback_data=f"nav:{day + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None


def settings_keyboard(lang: str, subscribed: bool) -> InlineKeyboardMarkup:
    daily = t(lang, "btn_daily_off" if subscribed else "btn_daily_on")
    rows = [
        [InlineKeyboardButton(text=t(lang, "btn_change_campus"), callback_data="settings:campus")],
        [InlineKeyboardButton(text=t(lang, "btn_change_lang"), callback_data="settings:lang")],
        [InlineKeyboardButton(text=daily, callback_data="settings:subscribe")],
    ]
    if subscribed:
        rows.append([
            InlineKeyboardButton(text=t(lang, "btn_change_time"), callback_data="settings:time"),
            InlineKeyboardButton(text=t(lang, "btn_change_days"), callback_data="settings:days"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def notify_days_keyboard(days: str, lang: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=f"✅ {day_name(lang, day)[:2].capitalize()}" if str(day) in days else day_name(lang, day)[:2].capitalize(),
            callback_data=f"ndays:{day}",
        )
        for day in range(5)
    ]
    done = InlineKeyboardButton(text=t(lang, "btn_done"), callback_data="ndays:done")
    return InlineKeyboardMarkup(inline_keyboard=[buttons, [done]])
