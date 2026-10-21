<p align="center">
  <img src="src/pictures/hero.jpeg" alt="Zhralovka banner" width="100%">
</p>

<h1 align="center">Menubot</h1>

<p align="center">
  <a href="https://github.com/DenysHerasymchuk/zhralovka/actions/workflows/ci.yml"><img src="https://github.com/DenysHerasymchuk/zhralovka/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI/CD"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/aiogram-3.31-2CA5E0?logo=telegram&logoColor=white" alt="aiogram 3.31">
  <img src="https://img.shields.io/badge/SQLite-aiosqlite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/languages-EN%20%7C%20NL%20%7C%20UK-F5B800" alt="Languages: EN, NL, UK">
</p>

A Telegram bot that shows the Thomas More cafeteria menu. You pick your campus once and the bot remembers it, along with your language: English, Dutch or Ukrainian.

Menus come from `https://tmmenumanagement.azurewebsites.net/api/WeekMenu/<campus>`. Supported campuses: Antwerpen, De Nayer, Geel, Lier, Mechelen, Turnhout and Vorselaar.

The bot asks the menu service as little as possible. Each campus's week is fetched the first time someone needs it and then kept in memory until the following Monday at 07:00 (`NEW_WEEK_AT` in `menu/client.py`), when the next week is due. If the service has nothing yet, or still returns last week's menu, the bot asks again after 30 minutes until the new week appears. Changes the kitchen makes mid-week are not picked up. A restart or redeploy empties the memory, so the first request after one fetches again.

## Setup

Needs Python 3.11 or newer.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then put your token from @BotFather in API_TOKEN
.venv/bin/python main.py
```

The bot keeps each user's campus and language in SQLite. It creates the file on first start, at `DB_PATH` if set, otherwise `menubot.db` next to `main.py`.

## Running in Docker

```sh
docker build -t menubot .
docker run -d --name menubot --env-file .env -v menubot-data:/data --restart unless-stopped menubot
```

Logs go to stdout, so `docker logs menubot` (or Coolify's Logs tab) shows them. Each update is one line, like `user=42 message '/today' 85ms`. Set `LOG_LEVEL=DEBUG` to also see menu cache hits.

The database lives in the `menubot-data` volume, so it survives rebuilds. Run only one instance per bot token: Telegram polling doesn't allow two.

## CI/CD

`.github/workflows/ci.yml` runs the tests on every push and pull request. On a push to `main` it then builds the image, pushes it to `ghcr.io/<owner>/<repo>` (tags `latest` and `sha-<commit>`), and asks Coolify to redeploy.

Coolify setup:

1. Create a "Docker Image" resource with image `ghcr.io/<owner>/<repo>:latest`. If the package is private, add a GHCR registry login (a GitHub token with `read:packages`).
2. Set the `API_TOKEN` environment variable and add a persistent volume mounted at `/data`.
3. Copy the resource's deploy webhook URL and create an API token (Keys & Tokens).
4. In GitHub, go to Settings → Secrets → Actions and add `COOLIFY_WEBHOOK` (the URL) and `COOLIFY_TOKEN`. Without them the pipeline still publishes the image and skips the redeploy.

## Using it

The keyboard has three buttons: 🍽 Today, 📅 This week and ⚙️ Settings. In the week view you switch days with the buttons under the message. The same actions are available as commands:

| Command      | What it does                                |
|--------------|---------------------------------------------|
| `/start`     | Welcome message, asks for your campus       |
| `/today`     | Today's menu (alias `/menu`)                |
| `/week`      | This week, Monday to Friday                 |
| `/prices`    | Cafeteria prices (alias `/price`)           |
| `/subscribe` | Daily menu on or off                        |
| `/campus`    | Pick a different campus                     |
| `/language`  | Pick English, Dutch or Ukrainian            |
| `/help`      | List of commands                            |

New users get Dutch or Ukrainian if their Telegram app is set to one of those. Everyone else starts in English. ⚙️ Settings → 🌐 Language (or `/language`) shows the three languages, and choosing one turns the same message back into Settings in that language.

The menu service only publishes dish names in English and Dutch. The bot's own text, dates, categories and the `/prices` board have Ukrainian versions in `i18n/uk.py` (including `CATEGORIES`) and `UK_NAMES` in `menu/prices.py`. Dish names are translated by DeepL when `DEEPL_API_KEY` is set:

- Get a free key at [deepl.com/pro-api](https://www.deepl.com/pro-api). The free plan allows 500,000 characters a month; a week of dishes for one campus is about 2,000.
- Put it in `.env`, or in Coolify's environment variables, as `DEEPL_API_KEY`. Free keys end in `:fx` and the bot picks the matching DeepL host.
- Each dish name is translated once and stored in the `translations` table, so repeat dishes cost nothing and restarts don't re-translate.
- Every Monday at 07:00 (`NEW_WEEK_AT` in `menu/client.py`, the same time the cached menu expires) the bot fetches each campus's new week and translates its dishes ahead of time. Anything published later, or changed mid-week, is translated the first time a Ukrainian user opens it.
- Without a key, or if DeepL fails, dish names stay in English and the failure shows in the logs as `Dish translation to uk failed`.

Picking a language also sends a short "✅ Language: …" message. Telegram only replaces the bottom keyboard (Today / This week / Settings) when a new message arrives, so that message is what switches it.

### Prices

`/prices` shows the cafeteria's price board, one section at a time (🥪 sandwiches, 🍲 hot meals, 🥗 cold dishes, 🍰 desserts, 🥤 drinks). Every item lists three prices: 🎓 paying with a student or staff card, 🏢 with a TM intern card, and 💳 with Bancontact. The menu API has no prices, so the board lives in `menu/prices.py`, copied from the printed board. Edit that file when prices change; prices are in cents.

In ⚙️ Settings, 💶 Show prices turns on the student price after each category name (`🍽 Lunch of the day · €5,40`) in 🍽 Today, 📅 This week and the daily menu. It's off by default, saved per user, and never applies to menus shared with @zhralovkabot. `CATEGORY_PRICES` in the same file maps each menu category to a board row: soup to soup, lunch of the day and the suggestion menu to the daily special, salad to the salad bar menu, sandwich of today to the baguette snack, and snack to snack + fries.

### Daily menu

`/subscribe` (or the 🔔 button in ⚙️ Settings) sends you that day's menu with the ⬅️/➡️ buttons. By default it comes at 11:00 Brussels time, Monday to Friday. Send `/subscribe` again to stop.

While you're subscribed, ⚙️ Settings shows two more buttons:

- **⏰ Change time:** type a time like `10:45` (`9.05` and `10h45` work too). Send `/cancel` to keep the current one. The menu buttons keep working while the bot waits for the time.
- **📅 Change days:** tap weekdays on or off. At least one has to stay on.

Nothing is sent when the kitchen lists no dishes for the day or the menu service is down. Users who block the bot are unsubscribed automatically. The bot checks for due subscribers once a minute. A send time that falls while the bot is restarting is skipped for that day.

Each dish name is a link. Tapping it opens a Google Images search for that exact name in the browser.

### Inline mode

Share a menu in any chat without leaving it:

1. Type `@zhralovkabot ` (with the space) in a DM, group or channel comment.
2. A list shows the days from today through Friday for your campus (Monday to Friday at the weekend). Each entry has the date and its dish names.
3. Tap a day. The full menu is sent into the chat as you, marked "via @zhralovkabot". Dish names still link to Google Images. The shared message has no day buttons, because it's a snapshot of that one day.

Add a campus name to share another campus: `@zhralovkabot lier`, or just a prefix like `de na`. Your saved campus stays the same. If nothing matches, your own campus is used.

Someone who hasn't picked a campus gets an empty list with a **📍 Pick your campus first** button. It opens the bot, runs `/start`, and once they've picked a campus the inline list works.

Results are in the sender's language and cached for 5 minutes per user. When the menu service is down or a campus hasn't published its menu, the list is empty.

Turn it on once in @BotFather: send `/setinline`, pick the bot, and set the placeholder to `Campus (optional), e.g. Geel`.

## Layout

```
main.py              starts the bot and registers commands
config.py            settings from the environment (.env)
db.py                SQLite storage for campus and language
menu/models.py       Dish and Week, parsing the menu API response
menu/client.py       fetches the menu API, keeps each campus's week until next Monday 07:00
menu/prices.py       the cafeteria price board, edited by hand
i18n/en.py, nl.py    all bot text, one file per language
i18n/__init__.py     text lookup and language detection
formatting.py        turns a day's menu into a message
middleware.py        logs every update with user, action and duration
notifier.py          sends the daily menu to subscribers
keyboards/menu.py    reply and inline keyboards
handlers/            start, menu, settings, inline and fallback handlers; common.py has the user lookup
tests/               unit tests, network mocked
```

## Tests

```sh
.venv/bin/python -m unittest -v
```

The tests never call the real API. `tests/fixtures/geel.json` is a saved response from Geel, used to check the parser against real data.
