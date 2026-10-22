import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.exceptions import TelegramBadRequest, TelegramMigrateToChat
from aiogram.methods import GetChatMember, SendPhoto
from aiogram.types import ForceReply, ReplyKeyboardMarkup

import db
import commands
import notifier
from handlers import fallback, groups, menu, notify, settings, start
from handlers.common import is_admin
from i18n import TEXTS
from tests.helpers import (
    GROUP,
    TUESDAY,
    WEEK,
    HandlerTestCase,
    bot,
    callback,
    group_callback,
    group_message,
    message,
    sent_text,
)


def reply_keyboards(mock) -> list:
    """Every ReplyKeyboardMarkup the mock was asked to send, at any depth."""
    return [v for c in mock.mock_calls for v in (*c.args, *c.kwargs.values()) if isinstance(v, ReplyKeyboardMarkup)]


class NoBottomMenuInGroupsTest(HandlerTestCase):
    async def test_start_in_a_group_greets_the_group_without_a_keyboard(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/start")
        await start.start(msg)
        self.assertEqual(msg.answer_photo.await_args.kwargs["caption"], TEXTS["en"]["welcome_group"])
        self.assertIn("This group's campus is <b>Geel</b>", sent_text(msg))
        self.assertEqual(reply_keyboards(msg), [])

    async def test_start_in_a_dm_still_sends_the_keyboard(self):
        await db.set_campus(42, "Geel")
        msg = message("/start")
        await start.start(msg)
        self.assertEqual(len(reply_keyboards(msg)), 1)

    async def test_admin_picking_the_first_campus_gets_no_keyboard(self):
        cb = group_callback("campus:Lier", admin=True)
        await settings.save_campus(cb)
        self.assertEqual((await db.get_user(GROUP))[0], "Lier")
        self.assertIn("Send /today", sent_text(cb.message))
        self.assertEqual(reply_keyboards(cb.message), [])

    async def test_language_change_in_a_group_sends_no_keyboard_message(self):
        cb = group_callback("lang:nl", admin=True)
        await settings.save_lang(cb)
        self.assertEqual((await db.get_user(GROUP))[1], "nl")
        cb.message.answer.assert_not_awaited()

    async def test_campus_prompt_uses_group_wording(self):
        msg = group_message("/today")
        await menu.show_today(msg)
        self.assertEqual(msg.answer_photo.await_args.kwargs["caption"], TEXTS["en"]["pick_campus_group"])


class AdminOnlyTest(HandlerTestCase):
    async def test_member_cannot_open_settings(self):
        msg = group_message("/settings")
        await settings.show_settings(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["admins_only"])
        msg.answer_photo.assert_not_awaited()

    async def test_admin_opens_settings(self):
        msg = group_message("/settings", admin=True)
        await settings.show_settings(msg)
        self.assertIn("Settings", msg.answer_photo.await_args.kwargs["caption"])

    async def test_member_tapping_a_campus_gets_a_popup_and_nothing_changes(self):
        await db.set_campus(GROUP, "Geel")
        cb = group_callback("campus:Lier")
        await settings.save_campus(cb)
        self.assertEqual((await db.get_user(GROUP))[0], "Geel")
        cb.answer.assert_awaited_once_with(TEXTS["en"]["admins_only"], show_alert=True)

    async def test_member_cannot_subscribe_the_group(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/subscribe")
        await notify.subscribe(msg)
        self.assertFalse((await db.get_notify(GROUP))[0])

    async def test_member_cannot_change_days(self):
        cb = group_callback("ndays:1")
        await notify.toggle_day(cb)
        self.assertEqual((await db.get_notify(GROUP))[2], "01234")

    async def test_anonymous_admin_needs_no_lookup(self):
        msg = group_message("/settings")
        msg.sender_chat = SimpleNamespace(id=GROUP)
        self.assertTrue(await is_admin(msg))
        msg.bot.get_chat_member.assert_not_awaited()

    async def test_failed_lookup_counts_as_not_admin(self):
        msg = group_message("/settings")
        msg.bot.get_chat_member = AsyncMock(side_effect=TelegramBadRequest(GetChatMember(chat_id=GROUP, user_id=7), "nope"))
        self.assertFalse(await is_admin(msg))

    async def test_group_owner_is_an_admin(self):
        msg = group_message("/settings")
        msg.bot = bot("creator")
        self.assertTrue(await is_admin(msg))

    async def test_dm_never_checks(self):
        msg = message("/settings")
        await settings.show_settings(msg)
        msg.bot.get_chat_member.assert_not_awaited()
        self.assertIn("Settings", msg.answer_photo.await_args.kwargs["caption"])

    async def test_menus_stay_open_to_members(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/today")
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
        self.assertIn("<b>Tuesday</b>", msg.answer_photo.await_args.kwargs["caption"])
        msg.bot.get_chat_member.assert_not_awaited()


class GroupDailyMenuTest(HandlerTestCase):
    async def test_admin_subscribes_the_group(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/subscribe", admin=True)
        await notify.subscribe(msg)
        self.assertTrue((await db.get_notify(GROUP))[0])
        self.assertIn("post the menu here at 11:00", sent_text(msg))
        self.assertFalse((await db.get_notify(7))[0])  # the admin's own DM is untouched

    async def test_time_prompt_in_a_group_is_a_force_reply_to_the_admin(self):
        cb = group_callback("settings:time", admin=True)
        await notify.ask_time(cb, AsyncMock())
        text, kwargs = cb.message.answer.await_args.args[0], cb.message.answer.await_args.kwargs
        self.assertIn('<a href="tg://user?id=7">Sam</a>', text)
        self.assertIsInstance(kwargs["reply_markup"], ForceReply)
        self.assertTrue(kwargs["reply_markup"].selective)

    async def test_time_prompt_in_a_dm_is_plain(self):
        cb = callback("settings:time")
        await notify.ask_time(cb, AsyncMock())
        self.assertEqual(cb.message.answer.await_args.args[0], TEXTS["en"]["ask_time"])

    async def test_daily_menu_is_posted_in_the_group(self):
        await db.add_user(GROUP, "en")
        await db.set_campus(GROUP, "Geel")
        await db.set_subscribed(GROUP, True)
        b = bot()
        with patch("notifier.fetch_week", AsyncMock(return_value=WEEK)), patch("notifier.SEND_INTERVAL", 0):
            self.assertEqual(await notifier.send_due(b, TUESDAY, "11:00"), 1)
        self.assertEqual(b.send_photo.await_args.args[0], GROUP)

    async def test_daily_menu_follows_a_group_upgraded_to_supergroup(self):
        old, new = -42, -100999
        await db.add_user(old, "en")
        await db.set_campus(old, "Geel")
        await db.set_subscribed(old, True)
        b = bot()
        moved = TelegramMigrateToChat(SendPhoto(chat_id=old, photo="x"), "moved", migrate_to_chat_id=new)
        b.send_photo = AsyncMock(side_effect=[moved, MagicMock()])
        with patch("notifier.fetch_week", AsyncMock(return_value=WEEK)), patch("notifier.SEND_INTERVAL", 0):
            self.assertEqual(await notifier.send_due(b, TUESDAY, "11:00"), 1)
        self.assertEqual(b.send_photo.await_args.args[0], new)
        self.assertIsNone(await db.get_user(old))
        self.assertTrue((await db.get_notify(new))[0])


class GroupMembershipTest(HandlerTestCase):
    def update(self, language_code="nl"):
        event = MagicMock()
        event.chat = SimpleNamespace(id=GROUP, type="supergroup")
        event.from_user = SimpleNamespace(id=7, language_code=language_code)
        event.bot = bot()
        return event

    async def test_added_to_a_group_greets_and_asks_for_a_campus(self):
        event = self.update()
        await groups.added_to_group(event)
        captions = [c.kwargs["caption"] for c in event.bot.send_photo.await_args_list]
        self.assertEqual(captions, [TEXTS["nl"]["welcome_group"], TEXTS["nl"]["pick_campus_group"]])
        self.assertEqual(await db.get_user(GROUP), (None, "nl"))  # language of whoever added the bot

    async def test_readded_group_keeps_its_campus(self):
        await db.add_user(GROUP, "en")
        await db.set_campus(GROUP, "Geel")
        event = self.update()
        await groups.added_to_group(event)
        self.assertIn("<b>Geel</b>", event.bot.send_message.await_args.args[1])

    async def test_removed_from_a_group_stops_the_daily_menu(self):
        await db.set_subscribed(GROUP, True)
        await groups.removed_from_group(self.update())
        self.assertFalse((await db.get_notify(GROUP))[0])

    async def test_supergroup_upgrade_moves_settings(self):
        old = -42
        await db.add_user(old, "uk")
        await db.set_campus(old, "Lier")
        msg = group_message()
        msg.migrate_from_chat_id = old
        await groups.group_upgraded(msg)
        self.assertEqual(await db.get_user(GROUP), ("Lier", "uk"))
        self.assertIsNone(await db.get_user(old))


class FallbackTest(HandlerTestCase):
    async def test_silent_in_groups(self):
        msg = group_message("hello everyone")
        await fallback.fallback(msg)
        msg.answer.assert_not_awaited()
        self.assertIsNone(await db.get_user(GROUP))

    async def test_still_answers_in_dms(self):
        msg = message("hello")
        await fallback.fallback(msg)
        self.assertEqual(sent_text(msg), TEXTS["en"]["unknown"])


class CommandMenusTest(unittest.IsolatedAsyncioTestCase):
    async def test_each_audience_gets_its_own_list(self):
        b = MagicMock()
        b.set_my_commands = AsyncMock()
        await commands.set_commands(b)
        lists = {
            (type(c.kwargs["scope"]).__name__, c.kwargs["language_code"]): [x.command for x in c.args[0]]
            for c in b.set_my_commands.await_args_list
        }
        self.assertEqual(lists["BotCommandScopeAllGroupChats", None], ["today", "shortm", "week", "prices", "help"])
        self.assertIn("settings", lists["BotCommandScopeAllChatAdministrators", "uk"])
        self.assertNotIn("start", lists["BotCommandScopeAllChatAdministrators", None])
        self.assertIn("settings", lists["BotCommandScopeAllPrivateChats", "nl"])


if __name__ == "__main__":
    unittest.main()
