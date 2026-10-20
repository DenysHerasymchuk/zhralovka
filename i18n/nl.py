DAY_NAMES = ("maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag")
MONTHS = ("januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december")

TEXTS = {
    # Keyboards
    "btn_today": "🍽 Vandaag",
    "btn_week": "📅 Deze week",
    "btn_prev_day": "⬅️ Vorige dag",
    "btn_next_day": "Volgende dag ➡️",
    "btn_settings": "⚙️ Instellingen",
    "btn_change_campus": "📍 Andere campus",
    "btn_change_lang": "🌐 Language: English",
    "placeholder": "Honger?",

    # Onboarding
    "welcome": (
        "<b>Hoi {name} 👋</b>\n"
        "Ik lees het menu van de Thomas More-cafetaria voor je, dan hoef je "
        "niet helemaal naar het bord te lopen.\n\n"
        "<blockquote>🍽 <b>Vandaag</b>  wat er nu op het menu staat\n"
        "📅 <b>Deze week</b>  maandag tot vrijdag\n"
        "⚙️ <b>Instellingen</b>  campus en taal</blockquote>"
    ),
    "welcome_back": "📍 Je campus is <b>{campus}</b>. Tik op 🍽 Vandaag om te zien wat er op het menu staat.",
    "pick_campus": "📍 <b>Kies je campus</b>\nIk onthoud hem. Je kunt hem altijd aanpassen via ⚙️ Instellingen.",

    # Settings
    "settings": (
        "⚙️ <b>Instellingen</b>\n\n"
        "<blockquote>📍 Campus: <b>{campus}</b>\n"
        "🌐 Taal: <b>Nederlands</b></blockquote>"
    ),
    "no_campus": "nog niet gekozen",
    "campus_saved": "✅ <b>Campus ingesteld op {campus}</b>\nTik op 🍽 Vandaag om te zien wat er op het menu staat.",
    "lang_saved": "✅ <b>Overgeschakeld naar het Nederlands</b>",

    # Menu
    "weekend": (
        "😴 <b>Gesloten in het weekend</b>\n"
        "Het is {day}, dus de keuken is dicht. Via 📅 Deze week zie je het laatste menu."
    ),
    "no_menu": (
        "🗒 <b>Nog geen menu</b>\n"
        "{campus} heeft het menu van deze week nog niet gepubliceerd. "
        "Kijk later nog eens, of kies een andere campus via ⚙️ Instellingen."
    ),
    "no_dishes": "<i>Er staat niets gepland op {day}. Waarschijnlijk een vrije dag.</i>",

    # Inline mode
    "inline_pick_campus": "📍 Kies eerst je campus",
    "inline_no_dishes": "Niets gepland",

    # Errors
    "unavailable": (
        "⚠️ <b>Menu niet beschikbaar</b>\n"
        "Ik kan de menuservice nu niet bereiken. Probeer het over een minuutje opnieuw."
    ),
    "unknown": "🤔 Ik weet alleen iets over eten. Gebruik de knoppen hieronder, of stuur /help.",

    # Help and command menu
    "help": (
        "❓ <b>Wat ik kan</b>\n\n"
        "<blockquote>/today  menu van vandaag\n"
        "/week of /menu  blader door maandag tot vrijdag\n"
        "/campus  kies een andere campus\n"
        "/language  wissel naar Engels</blockquote>\n"
        "Om een menu te delen, typ mijn @gebruikersnaam in een chat en kies een dag. "
        "Zet er een campusnaam achter voor een andere campus.\n\n"
        "De menu's komen rechtstreeks van de Thomas More-keukens. Klopt er "
        "iets niet, dan ligt dat aan de keuken."
    ),
    "cmd_today": "Menu van vandaag",
    "cmd_week": "Menu van deze week",
    "cmd_campus": "Andere campus",
    "cmd_language": "Language: English",
    "cmd_help": "Wat deze bot kan",
    "cmd_start": "Opnieuw beginnen",
}
