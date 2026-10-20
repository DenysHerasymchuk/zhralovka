import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import CallbackQuery, Message

from middleware import log_updates


def update_with(event):
    return SimpleNamespace(event=event)


class LogUpdatesTest(unittest.IsolatedAsyncioTestCase):
    async def test_logs_user_action_and_duration(self):
        msg = MagicMock(spec=Message, text="/today", content_type="text")
        with self.assertLogs("bot.updates", "INFO") as logs:
            result = await log_updates(AsyncMock(return_value="ok"), update_with(msg), {"event_from_user": SimpleNamespace(id=42)})
        self.assertEqual(result, "ok")
        self.assertRegex(logs.output[0], r"INFO:bot.updates:user=42 message '/today' \d+ms")

    async def test_logs_failure_and_reraises(self):
        cb = MagicMock(spec=CallbackQuery, data="nav:2")
        with self.assertLogs("bot.updates", "ERROR") as logs, self.assertRaises(RuntimeError):
            await log_updates(AsyncMock(side_effect=RuntimeError), update_with(cb), {})
        self.assertIn("user=? callback 'nav:2' failed", logs.output[0])

    async def test_long_text_is_cut(self):
        msg = MagicMock(spec=Message, text="x" * 500, content_type="text")
        with self.assertLogs("bot.updates", "INFO") as logs:
            await log_updates(AsyncMock(), update_with(msg), {})
        self.assertNotIn("x" * 41, logs.output[0])


if __name__ == "__main__":
    unittest.main()
