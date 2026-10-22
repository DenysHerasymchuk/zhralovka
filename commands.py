from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
)

from i18n import LANGS, t

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
