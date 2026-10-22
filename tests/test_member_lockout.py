"""A regular group member must not be able to open, change or step through any settings."""

from unittest.mock import AsyncMock, patch

import db
from handlers import clear, notify, settings
from i18n import TEXTS
from tests.helpers import GROUP, HandlerTestCase, group_callback, group_message

LOCKED = TEXTS["en"]["admins_only"]

# Every settings button a member could tap, including ones forged with made-up data.
CALLBACKS = (
    (settings.ask_campus_from_settings, "settings:campus"),
    (settings.save_campus, "campus:Lier"),
    (settings.ask_lang_from_settings, "settings:lang"),
    (settings.save_lang, "lang:uk"),
    (settings.toggle_prices, "settings:prices"),
    (settings.show_access, "settings:access"),
    (settings.toggle_access, "access:today"),
    (settings.toggle_access, "access:done"),
    (notify.subscribe_from_settings, "settings:subscribe"),
    (notify.ask_time, "settings:time"),
    (notify.ask_days, "settings:days"),
    (notify.toggle_day, "ndays:1"),
    (notify.toggle_day, "ndays:done"),
)

COMMANDS = (
    (settings.show_settings, "/settings"),
    (settings.show_settings, "⚙️ Settings"),
    (settings.ask_campus, "/campus"),
    (settings.ask_lang, "/language"),
    (notify.subscribe, "/subscribe"),
    (clear.clear, "/clear"),
)


class MemberLockoutTest(HandlerTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        await db.add_user(GROUP, "en")
        await db.set_campus(GROUP, "Geel")
        self.before = await self.snapshot()

    async def snapshot(self):
        return (
            await db.get_user(GROUP),
            await db.get_notify(GROUP),
            await db.get_show_prices(GROUP),
            await db.get_admin_commands(GROUP),
        )

    async def test_every_settings_button_is_locked(self):
        for handler, data in CALLBACKS:
            with self.subTest(data):
                cb = group_callback(data)
                args = (cb, AsyncMock()) if handler is notify.ask_time else (cb,)
                await handler(*args)
                cb.answer.assert_awaited_once_with(LOCKED, show_alert=True)
                cb.message.edit_text.assert_not_awaited()
                cb.message.edit_caption.assert_not_called()
                cb.message.answer.assert_not_awaited()
                cb.message.answer_photo.assert_not_awaited()
                self.assertEqual(await self.snapshot(), self.before)

    async def test_every_settings_command_is_locked(self):
        for handler, text in COMMANDS:
            with self.subTest(text):
                msg = group_message(text)
                await handler(msg)
                msg.answer.assert_awaited_once_with(LOCKED)
                msg.answer_photo.assert_not_awaited()
                self.assertEqual(await self.snapshot(), self.before)

    async def test_time_prompt_cannot_be_started_by_a_member(self):
        state = AsyncMock()
        await notify.ask_time(group_callback("settings:time"), state)
        state.set_state.assert_not_awaited()

    async def test_time_is_not_saved_if_admin_rights_were_lost(self):
        state = AsyncMock()
        await notify.save_time(group_message("09:15"), state)
        state.clear.assert_awaited_once()
        self.assertEqual(await self.snapshot(), self.before)

    async def test_admin_passes_the_same_checks(self):
        cb = group_callback("settings:prices", admin=True)
        await settings.toggle_prices(cb)
        self.assertTrue(await db.get_show_prices(GROUP))

    async def test_check_asks_telegram_about_the_person_who_tapped(self):
        cb = group_callback("settings:prices", user_id=555)
        await settings.toggle_prices(cb)
        cb.bot.get_chat_member.assert_awaited_once_with(GROUP, 555)

    async def test_restricted_and_left_members_are_not_admins(self):
        for status in ("member", "restricted", "left", "kicked"):
            with self.subTest(status):
                cb = group_callback("settings:prices")
                cb.bot.get_chat_member = AsyncMock(return_value=type("M", (), {"status": status})())
                await settings.toggle_prices(cb)
                self.assertFalse(await db.get_show_prices(GROUP))
