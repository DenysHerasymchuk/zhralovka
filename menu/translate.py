import logging
import time

import aiohttp

import db
from config import DEEPL_API_KEY
from menu.client import MenuUnavailable, fetch_week
from menu.models import CAMPUSES, Week

# Languages the menu API doesn't cover, mapped to DeepL's target code.
TARGETS = {"uk": "UK"}
# After DeepL fails, show English without asking again for this long.
RETRY_AFTER = 30 * 60

log = logging.getLogger(__name__)

_failed_at = 0.0


def _deepl_url(key: str) -> str:
    host = "api-free.deepl.com" if key.endswith(":fx") else "api.deepl.com"
    return f"https://{host}/v2/translate"


async def _deepl(texts: list[str], target: str) -> list[str]:
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            _deepl_url(DEEPL_API_KEY),
            json={"text": texts, "source_lang": "EN", "target_lang": target},
            headers={"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"},
        ) as response:
            response.raise_for_status()
            return [t["text"] for t in (await response.json())["translations"]]


async def localize(week: Week, lang: str) -> Week:
    """The week with dish names in `lang`, translated once and cached; English if that fails."""
    global _failed_at
    target = TARGETS.get(lang)
    if not target or not DEEPL_API_KEY:
        return week

    names = sorted({dish.en for dishes in week.days.values() for dish in dishes if dish.en})
    known = await db.get_translations(names, lang)
    missing = [name for name in names if name not in known]
    if missing and time.time() - _failed_at > RETRY_AFTER:
        try:
            new = dict(zip(missing, await _deepl(missing, target)))
        except (aiohttp.ClientError, TimeoutError, KeyError, TypeError, ValueError) as exc:
            log.warning("Dish translation to %s failed, retrying in %d min: %r", lang, RETRY_AFTER // 60, exc)
            _failed_at = time.time()
            new = {}
        if new:
            await db.save_translations(new, lang)
            log.info("Translated %d dish names to %s", len(new), lang)
        known |= new

    return week._replace(days={
        day: [dish._replace(en=known.get(dish.en, dish.en)) for dish in dishes]
        for day, dishes in week.days.items()
    })


async def prewarm() -> None:
    """Translate every campus's current menu ahead of time; already-cached names cost nothing."""
    if not DEEPL_API_KEY:
        return
    for campus in CAMPUSES:
        try:
            week = await fetch_week(campus)
        except MenuUnavailable:
            continue
        if week:
            for lang in TARGETS:
                await localize(week, lang)
