import tempfile
import unittest
from pathlib import Path

import aiosqlite

import db


class DbTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        await db.init(Path(self.tmp.name) / "test.db")

    async def asyncTearDown(self):
        self.tmp.cleanup()

    async def test_unknown_user(self):
        self.assertIsNone(await db.get_user(1))

    async def test_add_user_keeps_existing_lang(self):
        await db.add_user(1, "nl")
        await db.add_user(1, "en")
        self.assertEqual(await db.get_user(1), (None, "nl"))

    async def test_set_campus_and_lang(self):
        await db.add_user(1, "en")
        await db.set_campus(1, "Geel")
        await db.set_lang(1, "nl")
        self.assertEqual(await db.get_user(1), ("Geel", "nl"))

    async def test_set_campus_overwrites(self):
        await db.set_campus(1, "Geel")
        await db.set_campus(1, "Lier")
        self.assertEqual(await db.get_user(1), ("Lier", "en"))

    async def test_notify_defaults(self):
        self.assertEqual(await db.get_notify(1), (False, "11:00", "01234"))
        await db.add_user(1, "en")
        self.assertEqual(await db.get_notify(1), (False, "11:00", "01234"))

    async def test_notify_settings_round_trip(self):
        await db.set_subscribed(1, True)
        await db.set_notify_time(1, "09:30")
        await db.set_notify_days(1, "024")
        self.assertEqual(await db.get_notify(1), (True, "09:30", "024"))

    async def test_subscribers_due_matches_time_and_day(self):
        await db.set_campus(1, "Geel")
        await db.set_subscribed(1, True)
        await db.set_notify_time(1, "09:30")
        await db.set_notify_days(1, "024")
        self.assertEqual(await db.subscribers_due(2, "09:30"), [(1, "Geel", "en", 0)])
        self.assertEqual(await db.subscribers_due(1, "09:30"), [])  # Tuesday is off
        self.assertEqual(await db.subscribers_due(2, "11:00"), [])

    async def test_subscribers_due_skips_unsubscribed_and_campusless(self):
        await db.set_campus(1, "Geel")
        await db.set_subscribed(2, True)
        self.assertEqual(await db.subscribers_due(0, "11:00"), [])

    async def test_old_database_gets_new_columns(self):
        path = Path(self.tmp.name) / "old.db"
        async with aiosqlite.connect(path) as conn:
            await conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, campus TEXT, lang TEXT NOT NULL DEFAULT 'en')")
            await conn.execute("INSERT INTO users VALUES (7, 'Lier', 'nl')")
            await conn.commit()
        await db.init(path)
        self.assertEqual(await db.get_user(7), ("Lier", "nl"))
        await db.set_subscribed(7, True)
        self.assertEqual(await db.subscribers_due(0, "11:00"), [(7, "Lier", "nl", 0)])
        self.assertFalse(await db.get_show_prices(7))

    async def test_show_prices_round_trip(self):
        self.assertFalse(await db.get_show_prices(1))
        await db.set_show_prices(1, True)
        self.assertTrue(await db.get_show_prices(1))


if __name__ == "__main__":
    unittest.main()
