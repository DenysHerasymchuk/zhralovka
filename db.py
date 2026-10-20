import aiosqlite

from config import DB_PATH


async def init(path=DB_PATH) -> None:
    global DB_PATH
    DB_PATH = path
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " user_id INTEGER PRIMARY KEY,"
            " campus TEXT,"
            " lang TEXT NOT NULL DEFAULT 'en',"
            " subscribed INTEGER NOT NULL DEFAULT 0)"
        )
        # Databases created before /subscribe existed lack the column.
        async with db.execute("PRAGMA table_info(users)") as cursor:
            columns = {row[1] for row in await cursor.fetchall()}
        if "subscribed" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN subscribed INTEGER NOT NULL DEFAULT 0")
        await db.commit()


async def get_user(user_id: int) -> tuple[str | None, str] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT campus, lang FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone()


async def add_user(user_id: int, lang: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang)
        )
        await db.commit()


async def _set(user_id: int, column: str, value: str | int) -> None:
    # column comes from the callers below, never from user input
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"INSERT INTO users (user_id, {column}) VALUES (?, ?) "
            f"ON CONFLICT(user_id) DO UPDATE SET {column} = excluded.{column}",
            (user_id, value),
        )
        await db.commit()


async def set_campus(user_id: int, campus: str) -> None:
    await _set(user_id, "campus", campus)


async def set_lang(user_id: int, lang: str) -> None:
    await _set(user_id, "lang", lang)


async def set_subscribed(user_id: int, subscribed: bool) -> None:
    await _set(user_id, "subscribed", int(subscribed))


async def is_subscribed(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT subscribed FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
    return bool(row and row[0])


async def subscribers() -> list[tuple[int, str, str]]:
    """(user_id, campus, lang) for every subscriber who has picked a campus."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, campus, lang FROM users WHERE subscribed = 1 AND campus IS NOT NULL"
        ) as cursor:
            return await cursor.fetchall()
