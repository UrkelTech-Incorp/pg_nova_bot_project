"""Configuration loaded from environment variables.

Copy ``.env.example`` to ``.env`` and fill in the values, or export the
variables in your shell / hosting provider.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# --- Core ---
# Bot token from @BotFather. Required to run the bot.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()

# Your personal Telegram user id. When set, only you can use the
# posting/admin commands. Use /whoami to discover your id.
_owner_raw = os.environ.get("OWNER_ID", "").strip()
OWNER_ID = int(_owner_raw) if _owner_raw.lstrip("-").isdigit() else None

# SQLite database file used to remember detected chats.
DATABASE_NAME = os.environ.get("DATABASE_NAME", "bot_data.db").strip()


# --- Inline link buttons ---
# Each button is (label, url). A button is only shown when its url is set,
# so leave any of these empty to hide the corresponding button.
BUTTONS = [
    ("📢 Telegram Channel", os.environ.get("CHANNEL_URL", "").strip()),
    ("🌐 Website", os.environ.get("WEBSITE_URL", "").strip()),
    ("💝 Donations", os.environ.get("DONATIONS_URL", "").strip()),
    ("📹 Virtual Cam Room", os.environ.get("CAM_ROOM_URL", "").strip()),
    ("✉️ Contact Me", os.environ.get("CONTACT_URL", "").strip()),
]


def configured_buttons():
    """Return only the buttons that have a non-empty URL."""
    return [(label, url) for label, url in BUTTONS if url]
