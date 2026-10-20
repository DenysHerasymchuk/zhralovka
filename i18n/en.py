DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

TEXTS = {
    # Keyboards
    "btn_today": "🍽 Today",
    "btn_week": "📅 This week",
    "btn_prev_day": "⬅️ Previous day",
    "btn_next_day": "Next day ➡️",
    "btn_settings": "⚙️ Settings",
    "btn_change_campus": "📍 Change campus",
    "btn_change_lang": "🌐 Taal: Nederlands",
    "btn_daily_on": "🔔 Send me the menu daily",
    "btn_daily_off": "🔕 Stop the daily menu",
    "placeholder": "Hungry?",

    # Onboarding
    "welcome": (
        "<b>Hi {name} 👋</b>\n"
        "I read the Thomas More cafeteria menu for you, so you don't have to "
        "walk over just to look at the board.\n\n"
        "<blockquote>🍽 <b>Today</b>  what's cooking right now\n"
        "📅 <b>This week</b>  Monday to Friday\n"
        "⚙️ <b>Settings</b>  campus and language</blockquote>"
    ),
    "welcome_back": "📍 Your campus is <b>{campus}</b>. Tap 🍽 Today to see what's for lunch.",
    "pick_campus": "📍 <b>Pick your campus</b>\nI'll remember it. You can change it any time in ⚙️ Settings.",

    # Settings
    "settings": (
        "⚙️ <b>Settings</b>\n\n"
        "<blockquote>📍 Campus: <b>{campus}</b>\n"
        "🌐 Language: <b>English</b>\n"
        "🔔 Daily menu: <b>{daily}</b></blockquote>"
    ),
    "no_campus": "not picked yet",
    "daily_on": "on",
    "daily_off": "off",
    "campus_saved": "✅ <b>Campus set to {campus}</b>\nTap 🍽 Today to see what's for lunch.",
    "lang_saved": "✅ <b>Switched to English</b>",
    "subscribed": "🔔 <b>Daily menu on</b>\nI'll send you the menu every weekday at {time}. Send /subscribe again to stop.",
    "unsubscribed": "🔕 <b>Daily menu off</b>\nSend /subscribe to turn it back on.",

    # Menu
    "weekend": (
        "😴 <b>Closed for the weekend</b>\n"
        "It's {day}, so the kitchen is off. 📅 This week still shows the latest menu."
    ),
    "no_menu": (
        "🗒 <b>No menu yet</b>\n"
        "{campus} hasn't published this week's menu. Check back later, or switch campus in ⚙️ Settings."
    ),
    "no_dishes": "<i>Nothing is listed for {day}. Probably a day off.</i>",

    # Inline mode
    "inline_pick_campus": "📍 Pick your campus first",
    "inline_no_dishes": "Nothing listed",

    # Errors
    "unavailable": (
        "⚠️ <b>Menu unavailable</b>\n"
        "I can't reach the menu service right now. Give it a minute and try again."
    ),
    "unknown": "🤔 I only know about food. Use the buttons below, or send /help.",

    # Help and command menu
    "help": (
        "❓ <b>What I can do</b>\n\n"
        "<blockquote>/today  today's menu\n"
        "/week or /menu  flip through Monday to Friday\n"
        "/subscribe  get the menu every weekday morning\n"
        "/campus  change your campus\n"
        "/language  switch to Dutch</blockquote>\n"
        "To share a menu, type my @username in any chat and pick a day. "
        "Add a campus name to see another campus.\n\n"
        "Menus come straight from the Thomas More kitchens. If something "
        "looks off, blame the kitchen."
    ),
    "cmd_today": "Today's menu",
    "cmd_week": "This week's menu",
    "cmd_subscribe": "Daily menu on/off",
    "cmd_campus": "Change campus",
    "cmd_language": "Taal: Nederlands",
    "cmd_help": "What this bot can do",
    "cmd_start": "Start over",
}
