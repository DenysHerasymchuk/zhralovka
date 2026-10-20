from i18n import en, nl, uk

LANGS = ("en", "nl", "uk")
LANG_NAMES = {"en": "🇬🇧 English", "nl": "🇳🇱 Nederlands", "uk": "🇺🇦 Українська"}
_LOCALES = {"en": en, "nl": nl, "uk": uk}
TEXTS = {lang: locale.TEXTS for lang, locale in _LOCALES.items()}


def t(lang: str, key: str, **kwargs) -> str:
    return TEXTS[lang][key].format(**kwargs)


def all_langs(key: str) -> set[str]:
    """Every translation of a key, for matching reply-keyboard button presses."""
    return {TEXTS[lang][key] for lang in LANGS}


def detect_lang(language_code: str | None) -> str:
    code = (language_code or "").lower()
    return next((lang for lang in ("nl", "uk") if code.startswith(lang)), "en")


def day_name(lang: str, weekday: int) -> str:
    return _LOCALES[lang].DAY_NAMES[weekday]


def day_short(lang: str, weekday: int) -> str:
    return _LOCALES[lang].SHORT_DAYS[weekday]


def category_name(lang: str, category_en: str) -> str | None:
    """A translation of a menu API category, for languages the API doesn't cover."""
    return getattr(_LOCALES[lang], "CATEGORIES", {}).get(category_en)


def month_name(lang: str, month: int) -> str:
    return _LOCALES[lang].MONTHS[month - 1]
