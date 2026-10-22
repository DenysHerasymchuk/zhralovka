import logging

from aiogram import F, Router
from aiogram.filters import JOIN_TRANSITION, LEAVE_TRANSITION, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated, Message

import db
import screens
from i18n import detect_lang, t
from keyboards.menu import campus_keyboard

log = logging.getLogger(__name__)
router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def added_to_group(event: ChatMemberUpdated):
    chat = event.chat.id
    row = await db.get_user(chat)
    if row:
        campus, lang = row
    else:
        # The group starts in the language of whoever added the bot.
        campus, lang = None, detect_lang(event.from_user.language_code)
        await db.add_user(chat, lang)
    log.info("Added to group %s by user %s", chat, event.from_user.id)
    await screens.send_to(event.bot, chat, "hero", t(lang, "welcome_group"))
    if campus:
        await event.bot.send_message(chat, t(lang, "welcome_back_group", campus=campus))
    else:
        await screens.send_to(event.bot, chat, "location", t(lang, "pick_campus_group"), reply_markup=campus_keyboard())


@router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def removed_from_group(event: ChatMemberUpdated):
    await db.set_subscribed(event.chat.id, False)
    log.info("Removed from group %s, daily menu off", event.chat.id)


@router.message(F.migrate_from_chat_id)
async def group_upgraded(message: Message):
    await db.move_chat(message.migrate_from_chat_id, message.chat.id)
    log.info("Group %s became supergroup %s", message.migrate_from_chat_id, message.chat.id)
