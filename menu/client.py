import logging
import time
from urllib.parse import quote

import aiohttp

from menu.models import Week, parse_week

API_URL = "https://tmmenumanagement.azurewebsites.net/api/WeekMenu/"
CACHE_TTL = 30 * 60

log = logging.getLogger(__name__)

_cache: dict[str, tuple[float, Week | None]] = {}


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
    if cached and time.monotonic() - cached[0] < CACHE_TTL:
        return cached[1]

    try:
        week = parse_week(await _get(API_URL + quote(campus)))
    except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError, IndexError) as exc:
        log.warning("Menu fetch failed for %s: %r", campus, exc)
        raise MenuUnavailable from exc

    _cache[campus] = (time.monotonic(), week)
    return week
