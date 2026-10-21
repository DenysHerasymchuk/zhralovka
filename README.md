<p align="center">
  <img src="src/pictures/hero.jpeg" alt="Zhralovka banner" width="100%">
</p>

<h1 align="center">Zhralovka</h1>

<p align="center">
  <a href="https://github.com/DenysHerasymchuk/zhralovka/actions/workflows/ci.yml"><img src="https://github.com/DenysHerasymchuk/zhralovka/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI/CD"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/aiogram-3.31-2CA5E0?logo=telegram&logoColor=white" alt="aiogram 3.31">
  <img src="https://img.shields.io/badge/SQLite-aiosqlite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/languages-EN%20%7C%20NL%20%7C%20UK-F5B800" alt="Languages: EN, NL, UK">
</p>

<p align="center">
  Telegram bot with the Thomas More cafeteria menu.<br>
  Pick your campus once, then get today's menu, the week, prices and a daily reminder.
</p>

## Commands

| Command      | What it does                         |
|--------------|--------------------------------------|
| `/today`     | Today's menu                         |
| `/week`      | Monday to Friday                     |
| `/prices`    | Cafeteria price board                |
| `/subscribe` | Daily menu on or off (default 11:00) |
| `/campus`    | Change campus                        |
| `/language`  | English, Dutch or Ukrainian          |

Type `@zhralovkabot` in any chat to share a day's menu there.

Campuses: Antwerpen, De Nayer, Geel, Lier, Mechelen, Turnhout, Vorselaar.

## Run it

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # add API_TOKEN from @BotFather
.venv/bin/python main.py
```

Or with Docker:

```sh
docker build -t menubot .
docker run -d --name menubot --env-file .env -v menubot-data:/data --restart unless-stopped menubot
```

| Variable        | Purpose                                              |
|-----------------|------------------------------------------------------|
| `API_TOKEN`     | Bot token (required)                                 |
| `DB_PATH`       | SQLite file, default `menubot.db`                    |
| `DEEPL_API_KEY` | Translates dish names to Ukrainian (free plan works) |
| `LOG_LEVEL`     | `DEBUG` also logs menu cache hits                    |

Run one instance per token. Telegram polling allows only one.

Tests: `.venv/bin/python -m unittest -v`

<details>
<summary>Deploy (GitHub Actions + Coolify)</summary>

Every push and PR runs the tests. A merge to `main` also builds the image, pushes it to `ghcr.io/<owner>/<repo>` (`latest` and `sha-<commit>`) and triggers a Coolify redeploy.

1. In Coolify, create a Docker Image resource for `ghcr.io/<owner>/<repo>:latest`. A private package needs a GHCR login with `read:packages`.
2. Set `API_TOKEN` and mount a volume at `/data`.
3. Copy the deploy webhook URL and create an API token.
4. Add both to GitHub Actions secrets as `COOLIFY_WEBHOOK` and `COOLIFY_TOKEN`. Without them the image still publishes and the redeploy is skipped.

For inline sharing, send `/setinline` to @BotFather once and set the placeholder to `Campus (optional), e.g. Geel`.

</details>

<details>
<summary>How it works</summary>

Menus come from `tmmenumanagement.azurewebsites.net/api/WeekMenu/<campus>`. Each campus's week is fetched once and cached until Monday 07:00 (`NEW_WEEK_AT` in `menu/client.py`). If the new week isn't out yet, the bot retries every 30 minutes. Mid-week kitchen changes aren't picked up, and a restart clears the cache.

The menu API only has English and Dutch dish names. With `DEEPL_API_KEY` set, each dish is translated once and stored in the `translations` table; new weeks are translated on Monday at 07:00. Without a key, dish names stay in English.

Prices aren't in the API. They live in `menu/prices.py` (in cents), copied from the printed board. Edit that file when prices change.

The daily menu skips days with no dishes or when the service is down. Users who block the bot are unsubscribed.

```
main.py           starts the bot
config.py         settings from .env
db.py             SQLite storage
menu/             API client, models, prices, translation
i18n/             bot text per language
handlers/         command, settings and inline handlers
notifier.py       daily menu sender
tests/            unit tests, network mocked
```

</details>
