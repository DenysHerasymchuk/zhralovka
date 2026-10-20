import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
