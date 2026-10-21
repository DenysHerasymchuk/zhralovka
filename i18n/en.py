DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
SHORT_DAYS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

TEXTS = {
    # Keyboards
    "btn_today": "🍽 Today",
    "btn_week": "📅 This week",
    "btn_prev_day": "⬅️ Previous day",
    "btn_next_day": "Next day ➡️",
    "btn_show_prices": "💶 Show prices",
    "btn_hide_prices": "💶 Hide prices",
    "btn_settings": "⚙️ Settings",
    "btn_change_campus": "📍 Change campus",
    "btn_change_lang": "🌐 Language",
    "btn_daily_on": "🔔 Send me the menu daily",
    "btn_daily_off": "🔕 Stop the daily menu",
    "btn_change_time": "⏰ Change time",
    "btn_change_days": "📅 Change days",
    "btn_done": "✅ Done",
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
        "💶 Prices in menus: <b>{prices}</b>\n"
        "🔔 Daily menu: <b>{daily}</b></blockquote>"
    ),
    "no_campus": "not picked yet",
    "daily_on": "on",
    "daily_off": "off",
    "campus_saved": "✅ <b>Campus set to {campus}</b>\nTap 🍽 Today to see what's for lunch.",
    "pick_lang": "🌐 <b>Choose your language</b>",
    "lang_saved": "✅ Language: English",
    "subscribed": (
        "🔔 <b>Daily menu on</b>\n"
        "I'll send you the menu at {time}. Change the time and days in ⚙️ Settings, "
        "or send /subscribe again to stop."
    ),
    "unsubscribed": "🔕 <b>Daily menu off</b>\nSend /subscribe to turn it back on.",
    "ask_time": "⏰ <b>When should I send it?</b>\nSend me a time, e.g. 10:45.",
    "bad_time": "🤔 That's not a time, so I kept the old one. Tap ⏰ Change time in ⚙️ Settings to try again, e.g. 10:45.",
    "time_saved": "✅ <b>Daily menu at {time}</b>",
    "time_cancelled": "OK, the time stays the same.",
    "pick_days": "📅 <b>Which days?</b>\nTap a day to turn it on or off.",
    "need_a_day": "Pick at least one day. To stop the daily menu, use 🔕 in Settings.",

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
        "<blockquote>/today or /menu  today's menu\n"
        "/week  flip through Monday to Friday\n"
        "/prices  cafeteria prices\n"
        "/subscribe  get the menu every weekday morning\n"
        "/settings  campus, language, prices, daily menu\n"
        "/campus  change your campus\n"
        "/language  change language</blockquote>\n"
        "To share a menu, type my @username in any chat and pick a day. "
        "Add a campus name to see another campus.\n\n"
        "Menus come straight from the Thomas More kitchens. If something "
        "looks off, blame the kitchen."
    ),
    "cmd_today": "Today's menu",
    "cmd_week": "This week's menu",
    "cmd_prices": "Cafeteria prices",
    "cmd_subscribe": "Daily menu on/off",
    "cmd_campus": "Change campus",
    "cmd_language": "Change language",
    "cmd_help": "What this bot can do",
    "cmd_start": "Start over",
    "campus_saved_group": "✅ <b>Campus set to {campus}</b>\nSend /today to see what's for lunch.",
    "cmd_settings": "Campus, language, daily menu",
    "admins_only": "🔒 Only group admins can change this.",
    "welcome_group": "<b>Hi everyone 👋</b>\nI post the Thomas More cafeteria menu right here.\n\n<blockquote>/today  today's menu\n/week  Monday to Friday\n/prices  cafeteria prices</blockquote>\nAdmins can set the campus and a daily menu in /settings.",
    "welcome_back_group": "📍 This group's campus is <b>{campus}</b>. Send /today to see what's for lunch.",
    "pick_campus_group": "📍 <b>Pick this group's campus</b>\nAn admin can change it later in /settings.",
}
