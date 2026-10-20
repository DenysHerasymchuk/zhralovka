from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultsButton,
    InputTextMessageContent,
)

from formatting import day_summary, day_title, format_day, pick_day
from handlers.common import profile
from handlers.menu import NO_PREVIEW, load_week, today
from i18n import t
from menu.models import CAMPUSES

CACHE_SECONDS = 300

router = Router()


def _campus_from_query(query: str) -> str | None:
    query = query.strip().lower()
    if not query:
        return None
    return next((c for c in CAMPUSES if c.lower().startswith(query)), None)


@router.inline_query()
async def inline_menu(inline_query: InlineQuery):
    saved_campus, lang = await profile(inline_query.from_user)
    campus = _campus_from_query(inline_query.query) or saved_campus
    if not campus:
        await inline_query.answer(
            [],
            cache_time=0,
            is_personal=True,
            button=InlineQueryResultsButton(text=t(lang, "inline_pick_campus"), start_parameter="campus"),
        )
        return

    week, problem = await load_week(campus, lang)
    if problem:
        await inline_query.answer([], cache_time=30, is_personal=True)
        return

    first_day, _ = pick_day(today())
    results = [
        InlineQueryResultArticle(
            id=f"{campus}:{week.start}:{day}:{lang}",
            title=f"{day_title(week, day, lang)} · {campus}",
            description=day_summary(week, day, lang) or t(lang, "inline_no_dishes"),
            input_message_content=InputTextMessageContent(
                message_text=format_day(week, day, lang, campus),
                link_preview_options=NO_PREVIEW,
            ),
        )
        for day in range(first_day, 5)
    ]
    await inline_query.answer(results, cache_time=CACHE_SECONDS, is_personal=True)
