import logging
import time
from datetime import datetime, timedelta
from datetime import time as clock
from urllib.parse import quote

import aiohttp

from config import TIMEZONE
from menu.models import Week, parse_week

API_URL = "https://tmmenumanagement.azurewebsites.net/api/WeekMenu/"
# A published week is kept until the next one is due; the kitchens publish by Monday morning.
NEW_WEEK_AT = clock(7, 0)
# No menu yet, or still last week's: ask again after this long.
RETRY_AFTER = 30 * 60

log = logging.getLogger(__name__)

# campus -> (valid until, as a Unix timestamp; the week)
_cache: dict[str, tuple[float, Week | None]] = {}


def _valid_until(week: Week | None, now: float) -> float:
    if week:
        next_week = datetime.combine(week.start + timedelta(days=7), NEW_WEEK_AT, TIMEZONE).timestamp()
        if next_week > now:
            return next_week
    return now + RETRY_AFTER


class MenuUnavailable(Exception):
    """The menu service could not be reached or sent something unreadable."""


async def _get(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()


async def fetch_week(campus: str) -> Week | None:
    cached = _cache.get(campus)
    if cached and time.time() < cached[0]:
        log.debug("Menu cache hit for %s", campus)
        return cached[1]

    try:
        week = parse_week(await _get(API_URL + quote(campus)))
    except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError, IndexError) as exc:
        log.warning("Menu fetch failed for %s: %r", campus, exc)
        raise MenuUnavailable from exc

    _cache[campus] = (_valid_until(week, time.time()), week)
    if week:
        log.info("Fetched menu for %s, week of %s", campus, week.start)
    else:
        log.info("No menu published for %s", campus)
    return week
