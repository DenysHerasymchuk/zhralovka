import logging

from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Chat, Message, ReplyKeyboardMarkup

import db
from i18n import detect_lang, t
from keyboards.menu import main_keyboard

log = logging.getLogger(__name__)

ADMIN_STATUSES = {"creator", "administrator"}
# Commands a group's admins can keep to themselves. Settings-type commands are always admins-only.
CONTROLLED_COMMANDS = ("today", "shortm", "week", "prices", "help")
# Buttons under a message follow the rule of the command that posted it.
BUTTON_COMMANDS = {"nav": "today", "day": "week", "hot": "shortm", "prices": "prices"}


def _chat(event: Message | CallbackQuery) -> Chat | None:
    if isinstance(event, CallbackQuery):
        return event.message.chat if event.message else None
    return event.chat


def chat_id(event: Message | CallbackQuery) -> int:
    """The chat whose settings apply: the DM itself, or the group a button was tapped in."""
    chat = _chat(event)
    return chat.id if chat else event.from_user.id


def in_group(event: Message | CallbackQuery) -> bool:
    chat = _chat(event)
    return chat is not None and chat.type in ("group", "supergroup")


def reply_keyboard(event: Message | CallbackQuery, lang: str) -> ReplyKeyboardMarkup | None:
    """The bottom menu for DMs. Groups never get one: it would pop up for every member."""
    return None if in_group(event) else main_keyboard(lang)


def campus_prompt(event: Message | CallbackQuery, lang: str) -> str:
    return t(lang, "pick_campus_group" if in_group(event) else "pick_campus")


async def profile(event: Message | CallbackQuery) -> tuple[str | None, str]:
    """(campus, lang) of the event's chat, registering the chat on first contact."""
    cid = chat_id(event)
    row = await db.get_user(cid)
    if row:
        return row
    lang = detect_lang(event.from_user.language_code)
    await db.add_user(cid, lang)
    log.info("New chat %s, lang=%s", cid, lang)
    return None, lang


async def is_admin(event: Message | CallbackQuery) -> bool:
    """Anyone may change a DM's settings; in a group only its admins may."""
    if not in_group(event):
        return True
    chat = _chat(event)
    sender_chat = getattr(event, "sender_chat", None)
    if sender_chat is not None and sender_chat.id == chat.id:
        return True  # an anonymous admin, posting as the group
    try:
        member = await event.bot.get_chat_member(chat.id, event.from_user.id)
    except TelegramAPIError as exc:
        log.warning("Admin check in chat %s failed: %r", chat.id, exc)
        return False
    return member.status in ADMIN_STATUSES


async def admin_only(event: Message | CallbackQuery, lang: str) -> bool:
    """True if the sender may change this chat's settings; otherwise tells them why not."""
    if await is_admin(event):
        return True
    if isinstance(event, CallbackQuery):
        await event.answer(t(lang, "admins_only"), show_alert=True)
    else:
        await event.answer(t(lang, "admins_only"))
    return False


async def may_use(event: Message | CallbackQuery, command: str, lang: str) -> bool:
    """False, after telling the member, if this group has kept the command to its admins."""
    if not in_group(event) or command not in await db.get_admin_commands(chat_id(event)):
        return True
    if await is_admin(event):
        return True
    text = t(lang, "command_admins_only", command=command)
    if isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)
    else:
        await event.answer(text)
    return False


def button_command(callback: CallbackQuery) -> str:
    return BUTTON_COMMANDS[callback.data.partition(":")[0]]
