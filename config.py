"""Configuration for the Telegram Bot Poster.

Values come from environment variables (a local ``.env`` file is loaded
automatically). Chats and link-button URLs are persisted to JSON files so the
web dashboard, CLI and listener all share the same state.
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()

# --- Core ---
# Token from @BotFather. Accept either name; never hardcode it.
BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or os.environ.get("TELEGRAM_BOT_TOKEN")
    or ""
).strip()

# Optional owner lock for the in-Telegram commands. Use /whoami to find your id.
_owner_raw = os.environ.get("OWNER_ID", "").strip()
OWNER_ID = int(_owner_raw) if _owner_raw.lstrip("-").isdigit() else None

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHATS_FILE = os.path.join(_BASE_DIR, "saved_chats.json")
LINKS_FILE = os.path.join(_BASE_DIR, "link_buttons.json")

# Web dashboard settings
WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.environ.get("WEB_PORT", "5000"))


# --- Saved chats persistence ---
def load_saved_chats():
    """Load saved chats from JSON file."""
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_chats(chats):
    """Save chats to JSON file."""
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump(chats, f, indent=2)


# --- Inline link buttons ---
# (key, label, env-var with the default URL). A button only renders when its
# URL is set, so leave any blank to hide it.
BUTTON_DEFS = [
    ("channel", "\U0001F4E2 Telegram Channel", "CHANNEL_URL"),
    ("website", "\U0001F310 Website", "WEBSITE_URL"),
    ("donations", "\U0001F49D Donations", "DONATIONS_URL"),
    ("cam_room", "\U0001F4F9 Virtual Cam Room", "CAM_ROOM_URL"),
    ("contact", "\u2709\uFE0F Contact Me", "CONTACT_URL"),
]
BUTTON_LABELS = {key: label for key, label, _ in BUTTON_DEFS}


def _default_links():
    return {key: os.environ.get(env, "").strip() for key, _, env in BUTTON_DEFS}


def load_links():
    """Load link-button URLs: file overrides, else environment defaults."""
    links = _default_links()
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, "r", encoding="utf-8") as f:
                stored = json.load(f)
            for key in links:
                if isinstance(stored.get(key), str):
                    links[key] = stored[key].strip()
        except (json.JSONDecodeError, OSError):
            pass
    return links


def save_links(links):
    """Persist link-button URLs (only known keys are kept)."""
    clean = {key: str(links.get(key, "")).strip() for key, _, _ in BUTTON_DEFS}
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)
    return clean


def configured_buttons():
    """Return ordered (label, url) pairs for buttons that have a URL set."""
    links = load_links()
    return [
        (BUTTON_LABELS[key], links[key])
        for key, _, _ in BUTTON_DEFS
        if links.get(key)
    ]
