from i18n import en, nl

LANGS = ("en", "nl")
_LOCALES = {"en": en, "nl": nl}
TEXTS = {lang: locale.TEXTS for lang, locale in _LOCALES.items()}


def t(lang: str, key: str, **kwargs) -> str:
    return TEXTS[lang][key].format(**kwargs)


def all_langs(key: str) -> set[str]:
    """Every translation of a key, for matching reply-keyboard button presses."""
    return {TEXTS[lang][key] for lang in LANGS}


def detect_lang(language_code: str | None) -> str:
    return "nl" if (language_code or "").startswith("nl") else "en"


def day_name(lang: str, weekday: int) -> str:
    return _LOCALES[lang].DAY_NAMES[weekday]


def month_name(lang: str, month: int) -> str:
    return _LOCALES[lang].MONTHS[month - 1]
