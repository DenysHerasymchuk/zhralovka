import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    BotCommandScopeChatAdministrators,
    BotCommandScopeDefault,
)

from i18n import LANGS, t

log = logging.getLogger(__name__)

COMMANDS = ("today", "shortm", "week", "prices", "subscribe", "settings", "campus", "language", "clear", "help", "start")
GROUP_COMMANDS = ("today", "shortm", "week", "prices", "help")
GROUP_ADMIN_COMMANDS = GROUP_COMMANDS + ("settings", "campus", "language", "subscribe", "clear")
# Telegram shows the most specific list: admins in a group see theirs, other members the plain group list.
COMMAND_SCOPES = (
    (BotCommandScopeDefault(), COMMANDS),
    (BotCommandScopeAllPrivateChats(), COMMANDS),
    (BotCommandScopeAllGroupChats(), GROUP_COMMANDS),
    (BotCommandScopeAllChatAdministrators(), GROUP_ADMIN_COMMANDS),
)


def command_list(commands, lang: str) -> list[BotCommand]:
    return [BotCommand(command=cmd, description=t(lang, f"cmd_{cmd}")) for cmd in commands]


async def set_commands(bot: Bot) -> None:
    for scope, commands in COMMAND_SCOPES:
        for lang in LANGS:
            await bot.set_my_commands(
                command_list(commands, lang),
                scope=scope,
                language_code=None if lang == "en" else lang,
            )


async def set_chat_commands(bot: Bot, chat_id: int, restricted: set[str]) -> None:
    """A group's own menus: members stop seeing commands kept for admins, admins keep the full list.

    With nothing restricted the group-specific menus are removed and the global group lists apply again.
    Both scopes are set because a chat-specific list would otherwise hide the admins' global one.
    """
    members = BotCommandScopeChat(chat_id=chat_id)
    admins = BotCommandScopeChatAdministrators(chat_id=chat_id)
    open_commands = [cmd for cmd in GROUP_COMMANDS if cmd not in restricted]
    try:
        for lang in LANGS:
            code = None if lang == "en" else lang
            if restricted:
                await bot.set_my_commands(command_list(open_commands, lang), scope=members, language_code=code)
                await bot.set_my_commands(command_list(GROUP_ADMIN_COMMANDS, lang), scope=admins, language_code=code)
            else:
                await bot.delete_my_commands(scope=members, language_code=code)
                await bot.delete_my_commands(scope=admins, language_code=code)
    except TelegramAPIError as exc:
        log.warning("Command menu update for chat %s failed: %r", chat_id, exc)
