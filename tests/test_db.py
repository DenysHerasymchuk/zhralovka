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

    async def test_subscribe_round_trip(self):
        await db.set_campus(1, "Geel")
        self.assertFalse(await db.is_subscribed(1))
        await db.set_subscribed(1, True)
        self.assertTrue(await db.is_subscribed(1))
        self.assertEqual(await db.subscribers(), [(1, "Geel", "en")])
        await db.set_subscribed(1, False)
        self.assertEqual(await db.subscribers(), [])

    async def test_subscribers_need_a_campus(self):
        await db.set_subscribed(1, True)
        self.assertEqual(await db.subscribers(), [])

    async def test_old_database_gets_subscribed_column(self):
        path = Path(self.tmp.name) / "old.db"
        async with aiosqlite.connect(path) as conn:
            await conn.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, campus TEXT, lang TEXT NOT NULL DEFAULT 'en')")
            await conn.execute("INSERT INTO users VALUES (7, 'Lier', 'nl')")
            await conn.commit()
        await db.init(path)
        self.assertEqual(await db.get_user(7), ("Lier", "nl"))
        await db.set_subscribed(7, True)
        self.assertEqual(await db.subscribers(), [(7, "Lier", "nl")])


if __name__ == "__main__":
    unittest.main()
