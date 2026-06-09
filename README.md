# pg_nova_bot_project

A Telegram bot that posts messages to the groups and channels you manage, with
inline link buttons attached to every post. It auto-detects chats the bot is
added to, and gives you **three** ways to drive it: an in-Telegram `/post` flow,
a web dashboard, and an interactive CLI.

## Features

- **Auto-detect chats** – the moment you add the bot to a group/channel it
  records that chat's id (and drops it again if the bot is removed). Activity in
  a chat is also picked up, so pre-existing chats are detected too.
- **Post anywhere** – send to a chat you pick, to *all* detected chats, or to a
  chat id you type.
- **Inline link buttons** on every post: Telegram channel, Website, Donations,
  Virtual cam room, and Contact me. Each button only appears if its URL is set,
  and the URLs are editable live from the web dashboard.
- **Owner-only** – set `OWNER_ID` so only you can use the in-Telegram `/post`.

> **Important:** A bot can only post to a chat it is a **member of**. Add the bot
> to each target group/channel and make it an **admin** with permission to post.
> Bots cannot read or post to chats you are personally subscribed to unless the
> bot itself is added.

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill it in (at minimum `BOT_TOKEN`):
   ```bash
   cp .env.example .env
   ```

## Running

Use the launcher to pick a mode, or run a component directly:

```bash
python run.py           # interactive menu
python listener.py      # always-on bot: auto-detect + in-Telegram /post
python web_dashboard.py # web dashboard at http://localhost:5000
python cli.py           # interactive command-line menu
```

The `Procfile` runs `listener.py` as a `worker` and `web_dashboard.py` as `web`.

### In-Telegram commands (listener)

| Command   | What it does                                       |
|-----------|----------------------------------------------------|
| `/start`  | Welcome message and help                           |
| `/post`   | Post a message (pick a chat / all / type an id)    |
| `/list`   | List every detected chat, with ids                 |
| `/id`     | Show the current chat's id                          |
| `/whoami` | Show your Telegram user id (use it for `OWNER_ID`)  |
| `/cancel` | Cancel the current action                          |

### Web dashboard

Manage chats (auto-detect / add by id / manual), edit the link-button URLs, and
send to selected/all chats. The "Link buttons" checkbox toggles whether the
buttons are attached to a given post.

## How it works

- Detected chats are stored in `saved_chats.json`.
- Link-button URLs are stored in `link_buttons.json` (defaults come from the
  `*_URL` environment variables).
- Both files are git-ignored so your ids and links stay local.
