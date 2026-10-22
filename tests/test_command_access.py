import unittest
from unittest.mock import AsyncMock, patch

import db
from commands import GROUP_ADMIN_COMMANDS, set_chat_commands
from handlers import groups, menu, prices, settings, start
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


def buttons(markup) -> list[str]:
    return [b.callback_data for row in markup.inline_keyboard for b in row]


class DefaultsTest(HandlerTestCase):
    async def test_everything_is_open_by_default(self):
        await db.set_campus(GROUP, "Geel")
        msg = group_message("/shortm")
        msg.reply = AsyncMock()
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_hot_meal(msg)
        self.assertIn(">Tuesday pasta</a>", msg.reply.await_args.args[0])
        msg.bot.get_chat_member.assert_not_awaited()  # open commands don't even check


class RestrictedCommandTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await db.set_campus(GROUP, "Geel")
        await db.set_admin_commands(GROUP, {"week", "shortm", "prices", "help"})

    async def test_member_gets_the_lock_reply_and_no_menu(self):
        msg = group_message("/week")
        await menu.show_week(msg)
        self.assertEqual(sent_text(msg), "🔒 Only admins can use /week here.")
        msg.answer_photo.assert_not_awaited()

    async def test_admin_still_gets_the_menu(self):
        msg = group_message("/week", admin=True)
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_week(msg)
        msg.answer_photo.assert_awaited_once()

    async def test_lock_reply_follows_the_groups_language(self):
        await db.set_lang(GROUP, "nl")
        msg = group_message("/help")
        await start.help_(msg)
        self.assertEqual(sent_text(msg), "🔒 Alleen beheerders kunnen /help hier gebruiken.")

    async def test_open_commands_stay_open(self):
        msg = group_message("/today")
        with patch("handlers.menu.today", return_value=TUESDAY), \
             patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_today(msg)
        msg.answer_photo.assert_awaited_once()

    async def test_buttons_follow_their_command(self):
        for data, handler in (("hot:2", menu.switch_hot_meal), ("day:2", menu.switch_day), ("prices:1", prices.switch_section)):
            cb = group_callback(data)
            with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
                await handler(cb)
            self.assertTrue(cb.answer.await_args.kwargs.get("show_alert"), data)
            cb.message.edit_text.assert_not_awaited()

    async def test_today_buttons_stay_open_when_only_others_are_restricted(self):
        cb = group_callback("nav:2")
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.switch_day(cb)
        cb.message.edit_text.assert_awaited_once()

    async def test_dms_are_never_restricted(self):
        await db.set_admin_commands(42, {"week"})  # can't happen through the UI, but must not matter
        msg = message("/week")
        await db.set_campus(42, "Geel")
        with patch("handlers.menu.fetch_week", AsyncMock(return_value=WEEK)):
            await menu.show_week(msg)
        msg.answer_photo.assert_awaited_once()


class AccessScreenTest(HandlerTestCase):
    async def test_button_shows_in_group_settings_only(self):
        group = group_message("/settings", admin=True)
        await settings.show_settings(group)
        self.assertIn("settings:access", buttons(group.answer_photo.await_args.kwargs["reply_markup"]))

        dm = message("/settings")
        await settings.show_settings(dm)
        self.assertNotIn("settings:access", buttons(dm.answer_photo.await_args.kwargs["reply_markup"]))

    async def test_admin_opens_the_list(self):
        cb = group_callback("settings:access", admin=True)
        await settings.show_access(cb)
        text, kwargs = cb.message.edit_text.await_args.args[0], cb.message.edit_text.await_args.kwargs
        self.assertEqual(text, TEXTS["en"]["command_access"])
        rows = [row[0].text for row in kwargs["reply_markup"].inline_keyboard]
        self.assertEqual(rows[:2], ["/today · 👥 Everyone", "/shortm · 👥 Everyone"])
        self.assertEqual(rows[-1], TEXTS["en"]["btn_done"])

    async def test_member_cannot_open_the_list(self):
        cb = group_callback("settings:access")
        await settings.show_access(cb)
        cb.message.edit_text.assert_not_awaited()
        cb.answer.assert_awaited_once_with(TEXTS["en"]["admins_only"], show_alert=True)

    async def test_hidden_in_dms_even_if_tapped(self):
        cb = callback("settings:access")
        await settings.show_access(cb)
        cb.message.edit_text.assert_not_awaited()

    async def test_tapping_toggles_and_redraws(self):
        cb = group_callback("access:week", admin=True)
        await settings.toggle_access(cb)
        self.assertEqual(await db.get_admin_commands(GROUP), {"week"})
        rows = [row[0].text for row in cb.message.edit_text.await_args.kwargs["reply_markup"].inline_keyboard]
        self.assertIn("/week · 🛡 Admins only", rows)

        cb = group_callback("access:week", admin=True)
        await settings.toggle_access(cb)
        self.assertEqual(await db.get_admin_commands(GROUP), set())

    async def test_member_cannot_toggle(self):
        cb = group_callback("access:week")
        await settings.toggle_access(cb)
        self.assertEqual(await db.get_admin_commands(GROUP), set())

    async def test_settings_commands_cannot_be_opened_up(self):
        cb = group_callback("access:settings", admin=True)
        await settings.toggle_access(cb)
        self.assertEqual(await db.get_admin_commands(GROUP), set())

    async def test_done_goes_back_to_settings(self):
        cb = group_callback("access:done", admin=True)
        await settings.toggle_access(cb)
        self.assertIn("Settings", cb.message.edit_text.await_args.args[0])


class GroupCommandMenuTest(HandlerTestCase):
    def lists(self, b):
        return {
            (type(c.kwargs["scope"]).__name__, c.kwargs["language_code"]): [x.command for x in c.args[0]]
            for c in b.set_my_commands.await_args_list
        }

    async def test_members_lose_restricted_commands_admins_keep_all(self):
        b = bot()
        await set_chat_commands(b, GROUP, {"week", "help"})
        lists = self.lists(b)
        self.assertEqual(lists["BotCommandScopeChat", None], ["today", "shortm", "prices"])
        self.assertEqual(lists["BotCommandScopeChatAdministrators", "nl"], list(GROUP_ADMIN_COMMANDS))
        self.assertEqual(b.set_my_commands.await_args.kwargs["scope"].chat_id, GROUP)

    async def test_opening_everything_removes_the_groups_own_menus(self):
        b = bot()
        await set_chat_commands(b, GROUP, set())
        b.set_my_commands.assert_not_awaited()
        self.assertEqual(b.delete_my_commands.await_count, 6)  # 2 scopes x 3 languages

    async def test_toggle_updates_the_menu(self):
        cb = group_callback("access:shortm", admin=True)
        await settings.toggle_access(cb)
        self.assertNotIn("shortm", self.lists(cb.bot)["BotCommandScopeChat", None])

    async def test_supergroup_upgrade_restores_menus(self):
        await db.add_user(-42, "en")
        await db.set_admin_commands(-42, {"week"})
        msg = group_message()
        msg.migrate_from_chat_id = -42
        await groups.group_upgraded(msg)
        self.assertEqual(await db.get_admin_commands(GROUP), {"week"})
        self.assertNotIn("week", self.lists(msg.bot)["BotCommandScopeChat", None])


if __name__ == "__main__":
    unittest.main()
