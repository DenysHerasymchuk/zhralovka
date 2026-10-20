from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto, LinkPreviewOptions, Message

PICTURES_DIR = Path(__file__).parent / "src" / "pictures"
PICTURES = ("hero", "location", "today", "thisweek", "daily", "settings", "language", "share")

# Dish names are links; without this Telegram previews the first one.
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

# After the first upload Telegram knows each picture by file_id, so later sends skip the ~600 KB upload.
_file_ids: dict[str, str] = {}


def _photo(picture: str) -> str | FSInputFile:
    return _file_ids.get(picture) or FSInputFile(PICTURES_DIR / f"{picture}.jpeg")


def _remember(picture: str, sent) -> None:
    if isinstance(sent, Message) and sent.photo:
        _file_ids.setdefault(picture, sent.photo[-1].file_id)


async def send(message: Message, picture: str, text: str, reply_markup=None) -> None:
    sent = await message.answer_photo(_photo(picture), caption=text, reply_markup=reply_markup)
    _remember(picture, sent)


async def send_to(bot: Bot, chat_id: int, picture: str, text: str, reply_markup=None) -> None:
    sent = await bot.send_photo(chat_id, _photo(picture), caption=text, reply_markup=reply_markup)
    _remember(picture, sent)


async def edit(message: Message, text: str, reply_markup=None, picture: str | None = None) -> None:
    """Edit a screen in place; picture=None keeps the current one."""
    if not message.photo:
        await message.edit_text(text, reply_markup=reply_markup, link_preview_options=NO_PREVIEW)
    elif picture is None:
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        sent = await message.edit_media(InputMediaPhoto(media=_photo(picture), caption=text), reply_markup=reply_markup)
        _remember(picture, sent)
