# Menubot

A Telegram bot that shows the Thomas More cafeteria menu. You pick your campus once and the bot remembers it, along with whether you want the menu in English or Dutch.

Menus come from `https://tmmenumanagement.azurewebsites.net/api/WeekMenu/<campus>`. Supported campuses: Antwerpen, De Nayer, Geel, Lier, Mechelen, Turnhout and Vorselaar.

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
| `/today`     | Today's menu                                |
| `/week`      | This week, Monday to Friday (alias `/menu`) |
| `/subscribe` | Daily menu on or off                        |
| `/campus`    | Pick a different campus                     |
| `/language`  | Switch between English and Dutch            |
| `/help`      | List of commands                            |

New users get Dutch if their Telegram app is set to Dutch. Everyone else starts in English.

### Daily menu

`/subscribe` (or the 🔔 button in ⚙️ Settings) sends you that day's menu every weekday at 11:00 Brussels time, with the ⬅️/➡️ buttons. Send it again to stop. Nothing is sent when the kitchen lists no dishes for the day or the menu service is down. Users who block the bot are unsubscribed automatically. Set `DAILY_AT` (for example `10:30`) to change the time.

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
menu/client.py       fetches the menu API, caches each campus for 30 minutes
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
