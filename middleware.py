import logging
import time
from typing import Any, Awaitable, Callable

from aiogram.types import CallbackQuery, InlineQuery, Message, TelegramObject, Update

log = logging.getLogger("bot.updates")

MAX_TEXT = 40


def _describe(event: TelegramObject) -> str:
    if isinstance(event, Message):
        text = event.text or f"<{event.content_type}>"
        return f"message {text[:MAX_TEXT]!r}"
    if isinstance(event, CallbackQuery):
        return f"callback {event.data!r}"
    if isinstance(event, InlineQuery):
        return f"inline {event.query[:MAX_TEXT]!r}"
    return type(event).__name__


async def log_updates(
    handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
    update: Update,
    data: dict[str, Any],
) -> Any:
    user = data.get("event_from_user")
    who = f"user={user.id}" if user else "user=?"
    what = _describe(update.event)
    start = time.perf_counter()
    try:
        result = await handler(update, data)
    except Exception:
        # aiogram logs the traceback; this line ties the failure to the user and action.
        log.error("%s %s failed after %.0fms", who, what, (time.perf_counter() - start) * 1000)
        raise
    log.info("%s %s %.0fms", who, what, (time.perf_counter() - start) * 1000)
    return result
