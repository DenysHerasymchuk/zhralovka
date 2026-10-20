import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import db
import screens
from handlers.common import profile
from handlers.settings import settings_view
from i18n import t
from keyboards.menu import campus_keyboard, notify_days_keyboard

TIME_PATTERN = re.compile(r"(\d{1,2})[:.h](\d{2})")
WEEKDAYS = {"0", "1", "2", "3", "4"}

log = logging.getLogger(__name__)
router = Router()


class NotifyForm(StatesGroup):
    time = State()


def parse_time(text: str) -> str | None:
    match = TIME_PATTERN.fullmatch(text.strip().lower())
    if not match:
        return None
    hour, minute = int(match[1]), int(match[2])
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02}:{minute:02}"


async def toggle_subscription(user_id: int) -> tuple[bool, str]:
    subscribed, hhmm, _ = await db.get_notify(user_id)
    subscribed = not subscribed
    await db.set_subscribed(user_id, subscribed)
    log.info("User %s %s the daily menu", user_id, "subscribed to" if subscribed else "unsubscribed from")
    return subscribed, hhmm


@router.message(Command("subscribe"))
async def subscribe(message: Message):
    campus, lang = await profile(message.from_user)
    if not campus:
        await screens.send(message, "location", t(lang, "pick_campus"), reply_markup=campus_keyboard())
        return
    subscribed, hhmm = await toggle_subscription(message.from_user.id)
    await message.answer(t(lang, "subscribed", time=hhmm) if subscribed else t(lang, "unsubscribed"))


@router.callback_query(F.data == "settings:subscribe")
async def subscribe_from_settings(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    if not campus:
        await screens.edit(callback.message, t(lang, "pick_campus"), reply_markup=campus_keyboard(), picture="location")
        await callback.answer()
        return
    await toggle_subscription(callback.from_user.id)
    await screens.edit(callback.message, **await settings_view(callback.from_user.id, campus, lang))
    await callback.answer()


@router.callback_query(F.data == "settings:time")
async def ask_time(callback: CallbackQuery, state: FSMContext):
    _, lang = await profile(callback.from_user)
    await state.set_state(NotifyForm.time)
    await callback.message.answer(t(lang, "ask_time"))
    await callback.answer()


@router.message(NotifyForm.time, Command("cancel"))
async def cancel_time(message: Message, state: FSMContext):
    _, lang = await profile(message.from_user)
    await state.clear()
    await message.answer(t(lang, "time_cancelled"))


@router.message(NotifyForm.time, F.text)
async def save_time(message: Message, state: FSMContext):
    _, lang = await profile(message.from_user)
    hhmm = parse_time(message.text)
    if not hhmm:
        await message.answer(t(lang, "bad_time"))
        return
    await db.set_notify_time(message.from_user.id, hhmm)
    await state.clear()
    log.info("User %s set the daily menu to %s", message.from_user.id, hhmm)
    await message.answer(t(lang, "time_saved", time=hhmm))


@router.callback_query(F.data == "settings:days")
async def ask_days(callback: CallbackQuery):
    _, lang = await profile(callback.from_user)
    _, _, days = await db.get_notify(callback.from_user.id)
    await screens.edit(callback.message, t(lang, "pick_days"), reply_markup=notify_days_keyboard(days, lang))
    await callback.answer()


@router.callback_query(F.data.startswith("ndays:"))
async def toggle_day(callback: CallbackQuery):
    campus, lang = await profile(callback.from_user)
    choice = callback.data.removeprefix("ndays:")
    if choice == "done":
        await screens.edit(callback.message, **await settings_view(callback.from_user.id, campus, lang))
        await callback.answer()
        return
    if choice not in WEEKDAYS:
        await callback.answer()
        return

    _, _, days = await db.get_notify(callback.from_user.id)
    days = days.replace(choice, "") if choice in days else "".join(sorted(days + choice))
    if not days:
        await callback.answer(t(lang, "need_a_day"), show_alert=True)
        return
    await db.set_notify_days(callback.from_user.id, days)
    await screens.edit(callback.message, t(lang, "pick_days"), reply_markup=notify_days_keyboard(days, lang))
    await callback.answer()
