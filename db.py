import aiosqlite

from config import DB_PATH

DEFAULT_TIME, DEFAULT_DAYS = "11:00", "01234"

# Added after the first release; init() adds any that an older database lacks.
LATER_COLUMNS = {
    "subscribed": "INTEGER NOT NULL DEFAULT 0",
    "notify_time": f"TEXT NOT NULL DEFAULT '{DEFAULT_TIME}'",
    "notify_days": f"TEXT NOT NULL DEFAULT '{DEFAULT_DAYS}'",
    "show_prices": "INTEGER NOT NULL DEFAULT 0",
}


async def init(path=DB_PATH) -> None:
    global DB_PATH
    DB_PATH = path
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            " user_id INTEGER PRIMARY KEY,"
            " campus TEXT,"
            " lang TEXT NOT NULL DEFAULT 'en')"
        )
        async with db.execute("PRAGMA table_info(users)") as cursor:
            existing = {row[1] for row in await cursor.fetchall()}
        for column, definition in LATER_COLUMNS.items():
            if column not in existing:
                await db.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
        await db.execute(
            "CREATE TABLE IF NOT EXISTS translations ("
            " source TEXT NOT NULL,"
            " lang TEXT NOT NULL,"
            " text TEXT NOT NULL,"
            " PRIMARY KEY (source, lang))"
        )
        await db.commit()


async def get_translations(sources: list[str], lang: str) -> dict[str, str]:
    if not sources:
        return {}
    marks = ", ".join("?" * len(sources))
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            f"SELECT source, text FROM translations WHERE lang = ? AND source IN ({marks})", (lang, *sources)
        ) as cursor:
            return dict(await cursor.fetchall())


async def save_translations(pairs: dict[str, str], lang: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            "INSERT OR REPLACE INTO translations (source, lang, text) VALUES (?, ?, ?)",
            [(source, lang, text) for source, text in pairs.items()],
        )
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


async def set_show_prices(user_id: int, show: bool) -> None:
    await _set(user_id, "show_prices", int(show))


async def get_show_prices(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT show_prices FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
    return bool(row and row[0])


async def set_notify_time(user_id: int, hhmm: str) -> None:
    await _set(user_id, "notify_time", hhmm)


async def set_notify_days(user_id: int, days: str) -> None:
    await _set(user_id, "notify_days", days)


async def get_notify(user_id: int) -> tuple[bool, str, str]:
    """(subscribed, "HH:MM", weekday digits like "01234")."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT subscribed, notify_time, notify_days FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
    if not row:
        return False, DEFAULT_TIME, DEFAULT_DAYS
    return bool(row[0]), row[1], row[2]


async def subscribers_due(weekday: int, hhmm: str) -> list[tuple[int, str, str, int]]:
    """(user_id, campus, lang, show_prices) for subscribers due at this weekday and minute."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, campus, lang, show_prices FROM users"
            " WHERE subscribed = 1 AND campus IS NOT NULL"
            " AND notify_time = ? AND instr(notify_days, ?) > 0",
            (hhmm, str(weekday)),
        ) as cursor:
            return await cursor.fetchall()
