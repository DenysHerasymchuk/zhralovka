DAY_NAMES = ("maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag")
SHORT_DAYS = ("Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo")
MONTHS = ("januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december")

TEXTS = {
    # Keyboards
    "btn_today": "🍽 Vandaag",
    "btn_week": "📅 Deze week",
    "btn_prev_day": "⬅️ Vorige dag",
    "btn_next_day": "Volgende dag ➡️",
    "btn_show_prices": "💶 Toon prijzen",
    "btn_hide_prices": "💶 Verberg prijzen",
    "btn_settings": "⚙️ Instellingen",
    "btn_change_campus": "📍 Andere campus",
    "btn_change_lang": "🌐 Taal",
    "btn_daily_on": "🔔 Stuur me elke dag het menu",
    "btn_daily_off": "🔕 Stop het dagelijkse menu",
    "btn_change_time": "⏰ Ander tijdstip",
    "btn_change_days": "📅 Andere dagen",
    "btn_done": "✅ Klaar",
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
        "🌐 Taal: <b>Nederlands</b>\n"
        "💶 Prijzen in menu's: <b>{prices}</b>\n"
        "🔔 Dagelijks menu: <b>{daily}</b></blockquote>"
    ),
    "no_campus": "nog niet gekozen",
    "daily_on": "aan",
    "daily_off": "uit",
    "campus_saved": "✅ <b>Campus ingesteld op {campus}</b>\nTik op 🍽 Vandaag om te zien wat er op het menu staat.",
    "pick_lang": "🌐 <b>Kies je taal</b>",
    "lang_saved": "✅ Taal: Nederlands",
    "subscribed": (
        "🔔 <b>Dagelijks menu aan</b>\n"
        "Ik stuur je het menu om {time}. Tijdstip en dagen pas je aan via ⚙️ Instellingen, "
        "of stuur /subscribe opnieuw om te stoppen."
    ),
    "unsubscribed": "🔕 <b>Dagelijks menu uit</b>\nStuur /subscribe om het weer aan te zetten.",
    "ask_time": "⏰ <b>Wanneer moet ik het sturen?</b>\nStuur me een tijdstip, bv. 10:45.",
    "bad_time": "🤔 Dat is geen tijdstip, dus het oude blijft. Tik op ⏰ Ander tijdstip in ⚙️ Instellingen om het opnieuw te proberen, bv. 10:45.",
    "time_saved": "✅ <b>Dagelijks menu om {time}</b>",
    "time_cancelled": "Oké, het tijdstip blijft hetzelfde.",
    "pick_days": "📅 <b>Welke dagen?</b>\nTik op een dag om hem aan of uit te zetten.",
    "need_a_day": "Kies minstens één dag. Wil je het dagelijkse menu stoppen, gebruik dan 🔕 in Instellingen.",

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


    # Errors
    "unavailable": (
        "⚠️ <b>Menu niet beschikbaar</b>\n"
        "Ik kan de menuservice nu niet bereiken. Probeer het over een minuutje opnieuw."
    ),
    "unknown": "🤔 Ik weet alleen iets over eten. Gebruik de knoppen hieronder, of stuur /help.",

    # Help and command menu
    "help": (
        "❓ <b>Wat ik kan</b>\n\n"
        "<blockquote>/today of /menu  menu van vandaag\n"
        "/shortm  alleen de warme maaltijd van vandaag\n"
        "/week  blader door maandag tot vrijdag\n"
        "/prices  prijzen in de cafetaria\n"
        "/subscribe  krijg elke weekdag 's ochtends het menu\n"
        "/settings  campus, taal, prijzen, dagelijks menu\n"
        "/campus  kies een andere campus\n"
        "/clear  verwijder de knoppen onderaan\n"
        "/language  kies een andere taal</blockquote>\n"
        "De menu's komen rechtstreeks van de Thomas More-keukens. Klopt er "
        "iets niet, dan ligt dat aan de keuken."
    ),
    "cmd_today": "Menu van vandaag",
    "cmd_week": "Menu van deze week",
    "cmd_prices": "Prijzen in de cafetaria",
    "cmd_subscribe": "Dagelijks menu aan/uit",
    "cmd_campus": "Andere campus",
    "cmd_language": "Andere taal",
    "cmd_help": "Wat deze bot kan",
    "cmd_start": "Opnieuw beginnen",
    "campus_saved_group": "✅ <b>Campus ingesteld op {campus}</b>\nStuur /today om te zien wat er op het menu staat.",
    "cmd_settings": "Campus, taal, dagelijks menu",
    "admins_only": "🔒 Alleen groepsbeheerders kunnen dit aanpassen.",
    "welcome_group": "<b>Hallo allemaal 👋</b>\nIk zet het menu van de Thomas More-cafetaria gewoon hier.\n\n<blockquote>/today  menu van vandaag\n/week  maandag tot vrijdag\n/prices  prijzen in de cafetaria</blockquote>\nBeheerders kiezen de campus en een dagelijks menu via /settings.",
    "welcome_back_group": "📍 De campus van deze groep is <b>{campus}</b>. Stuur /today om te zien wat er op het menu staat.",
    "pick_campus_group": "📍 <b>Kies de campus van deze groep</b>\nEen beheerder kan hem later aanpassen via /settings.",
    "subscribed_group": "🔔 <b>Dagelijks menu aan</b>\nIk zet het menu hier om {time}. Beheerders passen tijdstip en dagen aan via /settings, of sturen /subscribe opnieuw om te stoppen.",
    "ask_time_group": "⏰ <b>Wanneer moet ik het posten?</b>\n{name}, antwoord op dit bericht met een tijdstip, bv. 10:45.",
    "menu_cleared": "🧹 <b>Menu verwijderd</b>\nDe knoppen zijn weg. Stuur /start om ze terug te krijgen.",
    "menu_cleared_group": "🧹 <b>Menu verwijderd</b>\nAchtergebleven knoppen zijn hier voor iedereen weg.",
    "cmd_clear": "Menu onderaan verwijderen",
    "no_hot_meal": "🤷 Vandaag staat er geen warme maaltijd op het menu.",
    "cmd_shortm": "Warme maaltijd van vandaag, kort",
}
