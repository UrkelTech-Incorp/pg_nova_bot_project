# pg_nova_bot_project

A Telegram bot that posts messages to the groups and channels you manage, with
inline link buttons attached to every post.

## Features

- **Auto-detect chats** – the moment you add the bot to a group or channel, it
  records that chat's id (and removes it again if the bot is kicked). It also
  picks up chats from activity it sees, so pre-existing chats are detected too.
- **Post anywhere** – `/post` lets you pick a detected chat, post to *all*
  detected chats at once, or type a chat id manually.
- **Inline link buttons** on every post: Telegram channel, Website, Donations,
  Virtual cam room, and Contact me. Each button only appears if you configure
  its URL.
- **Owner-only** – set `OWNER_ID` so only you can post.

> **Important:** A bot can only post to a chat it is a **member of**. Add the
> bot to each target group/channel and make it an **admin** with permission to
> post messages. Bots cannot read or post to chats you are personally
> subscribed to unless the bot itself is added.

## Commands

| Command   | What it does                                        |
|-----------|-----------------------------------------------------|
| `/start`  | Welcome message and help                            |
| `/post`   | Start the posting flow (pick chat / all / type id)  |
| `/chats`  | List every chat the bot has detected, with ids      |
| `/id`     | Show the current chat's id                           |
| `/whoami` | Show your Telegram user id (use it for `OWNER_ID`)   |
| `/cancel` | Cancel the current action                           |

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables. Copy `.env.example` to `.env` and fill it in:
   ```bash
   cp .env.example .env
   ```
   At minimum set `BOT_TOKEN`. Set `OWNER_ID` (get it via `/whoami`) to lock the
   bot to yourself, and set any of the button URLs you want to show.
4. Run it:
   ```bash
   python main_bot.py
   ```

## How to use

1. Start a chat with your bot and send `/whoami`; put the id in `OWNER_ID`.
2. Add the bot to a channel/group **as an admin**. It is detected automatically
   (`/chats` to confirm).
3. Send `/post`, choose a target, then send the message text. The bot posts it
   with your link buttons attached.

## Deployment

The included `Procfile` (`worker: python main_bot.py`) runs the bot as a polling
worker on platforms like Heroku/Railway. Set the same environment variables in
your host's config.
