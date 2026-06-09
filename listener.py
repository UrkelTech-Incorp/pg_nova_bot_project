#!/usr/bin/env python3
"""Telegram listener / poster bot (the always-on worker).

Responsibilities:
* Auto-detect every group/channel the bot is added to and save its id.
* Let the owner post from inside Telegram via /post — pick a saved chat, post
  to all of them, or type a chat id — with the configured link buttons attached.

The web dashboard (web_dashboard.py) and CLI (cli.py) are alternative front
ends that share the same saved_chats.json / link_buttons.json state.
"""
import functools
import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot_core import build_link_keyboard
from config import BOT_TOKEN, OWNER_ID, load_saved_chats, save_chats

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CHOOSE_CHAT, ENTER_ID, ENTER_TEXT = range(3)

_PRESENT_STATUSES = {"member", "administrator", "creator", "restricted"}
_GROUPISH = {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _remember_chat(chat) -> None:
    """Persist a group/supergroup/channel chat to saved_chats.json."""
    if chat is None or chat.type not in _GROUPISH:
        return
    chats = load_saved_chats()
    key = str(chat.id)
    existing = chats.get(key, {})
    chats[key] = {
        "id": chat.id,
        "title": chat.title or "Unknown",
        "type": chat.type,
        "username": chat.username or "",
        "detected_at": existing.get("detected_at", datetime.now().isoformat()),
        "auto_detected": existing.get("auto_detected", True),
    }
    save_chats(chats)


def _forget_chat(chat_id) -> None:
    chats = load_saved_chats()
    if str(chat_id) in chats:
        del chats[str(chat_id)]
        save_chats(chats)


def _chat_label(info: dict) -> str:
    icon = "📣" if info.get("type") == ChatType.CHANNEL else "👥"
    return f"{icon} {info.get('title', 'Unknown')}"


def restricted(func):
    """Allow a handler only for the configured OWNER_ID (if one is set)."""

    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if OWNER_ID is not None and (user is None or user.id != OWNER_ID):
            if update.callback_query:
                await update.callback_query.answer(
                    "You are not authorized to use this bot.", show_alert=True
                )
            elif update.effective_message:
                await update.effective_message.reply_text("Sorry, this is a private bot.")
            return ConversationHandler.END
        return await func(update, context)

    return wrapper


# --------------------------------------------------------------------------- #
# Auto-detect handlers
# --------------------------------------------------------------------------- #
async def track_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """React to the bot being added to / removed from a chat."""
    result = update.my_chat_member
    if result is None:
        return
    chat = result.chat
    if result.new_chat_member.status in _PRESENT_STATUSES:
        _remember_chat(chat)
        logger.info("Detected chat %s (%s)", chat.id, chat.title)
    else:
        _forget_chat(chat.id)
        logger.info("Removed chat %s (%s)", chat.id, chat.title)


async def passive_detect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remember any group/channel we see activity in (catches pre-existing ones)."""
    _remember_chat(update.effective_chat)


# --------------------------------------------------------------------------- #
# Basic commands
# --------------------------------------------------------------------------- #
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_html(
        f"Hi {user.mention_html()}! I post messages to your groups and channels.\n\n"
        "Add me to a channel/group <b>as an admin</b> and I'll detect it "
        "automatically.\n\n"
        "Commands:\n"
        "/post – post a message (pick a chat or type an id)\n"
        "/list – list the chats I've detected\n"
        "/id – show the current chat's id\n"
        "/whoami – show your user id\n"
        "/cancel – cancel the current action"
    )


async def whoami_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        f"Your user id is: {update.effective_user.id}"
    )


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    # Also register the chat when the command is used inside a group/channel.
    _remember_chat(chat)
    await update.effective_message.reply_text(
        f"Chat id: {chat.id}\nType: {chat.type}\n"
        f"Title: {chat.title or chat.full_name or 'N/A'}"
    )


@restricted
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chats = load_saved_chats()
    if not chats:
        await update.effective_message.reply_text(
            "I haven't detected any chats yet. Add me to a group or channel "
            "as an admin first."
        )
        return
    lines = ["Detected chats:\n"]
    for info in chats.values():
        handle = f" (@{info['username']})" if info.get("username") else ""
        lines.append(f"{_chat_label(info)}{handle}\n   id: {info['id']}")
    await update.effective_message.reply_text("\n".join(lines))


# --------------------------------------------------------------------------- #
# /post conversation
# --------------------------------------------------------------------------- #
@restricted
async def post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chats = load_saved_chats()
    keyboard = [
        [InlineKeyboardButton(_chat_label(info), callback_data=f"chat:{info['id']}")]
        for info in chats.values()
    ]
    if chats:
        keyboard.append(
            [InlineKeyboardButton("📨 All detected chats", callback_data="chat:all")]
        )
    keyboard.append(
        [InlineKeyboardButton("✏️ Enter chat id manually", callback_data="chat:manual")]
    )
    keyboard.append([InlineKeyboardButton("✖️ Cancel", callback_data="chat:cancel")])

    prompt = (
        "Where should I post?\nPick a chat below:"
        if chats
        else "I haven't detected any chats yet.\nYou can still enter a chat id manually:"
    )
    await update.effective_message.reply_text(
        prompt, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CHOOSE_CHAT


@restricted
async def choose_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data.split(":", 1)[1]

    if data == "cancel":
        await query.edit_message_text("Cancelled.")
        return ConversationHandler.END

    if data == "manual":
        await query.edit_message_text("Send me the chat id (e.g. -1001234567890).")
        return ENTER_ID

    if data == "all":
        context.user_data["targets"] = [info["id"] for info in load_saved_chats().values()]
        label = "all detected chats"
    else:
        context.user_data["targets"] = [int(data)]
        info = load_saved_chats().get(data)
        label = _chat_label(info) if info else str(data)

    await query.edit_message_text(
        f"Target: {label}\n\nNow send me the message text to post."
    )
    return ENTER_TEXT


@restricted
async def enter_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.effective_message.text.strip()
    try:
        chat_id = int(raw)
    except ValueError:
        await update.effective_message.reply_text(
            "That doesn't look like a numeric chat id. Try again, or /cancel."
        )
        return ENTER_ID
    context.user_data["targets"] = [chat_id]
    await update.effective_message.reply_text(
        f"Target: {chat_id}\n\nNow send me the message text to post."
    )
    return ENTER_TEXT


@restricted
async def enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.effective_message.text
    targets = context.user_data.get("targets", [])
    if not targets:
        await update.effective_message.reply_text("No target chat. Start over with /post.")
        return ConversationHandler.END

    keyboard = build_link_keyboard()
    ok, failed = [], []
    for chat_id in targets:
        try:
            await context.bot.send_message(
                chat_id=chat_id, text=text, reply_markup=keyboard
            )
            ok.append(chat_id)
        except Exception as exc:  # noqa: BLE001 - surface any send failure to the user
            logger.warning("Failed to post to %s: %s", chat_id, exc)
            failed.append((chat_id, str(exc)))

    parts = []
    if ok:
        parts.append(f"✅ Posted to {len(ok)} chat(s).")
    if failed:
        detail = "\n".join(f"• {cid}: {err}" for cid, err in failed)
        parts.append(f"⚠️ Failed for {len(failed)} chat(s):\n{detail}")
    await update.effective_message.reply_text("\n\n".join(parts) or "Nothing happened.")

    context.user_data.pop("targets", None)
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("targets", None)
    await update.effective_message.reply_text("Cancelled.")
    return ConversationHandler.END


# --------------------------------------------------------------------------- #
# Wiring
# --------------------------------------------------------------------------- #
def build_application() -> Application:
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN is not set. Put it in a .env file or export it before running."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    post_conv = ConversationHandler(
        entry_points=[CommandHandler("post", post_start)],
        states={
            CHOOSE_CHAT: [CallbackQueryHandler(choose_chat, pattern=r"^chat:")],
            ENTER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)],
            ENTER_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("whoami", whoami_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(post_conv)

    app.add_handler(ChatMemberHandler(track_membership, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(
        MessageHandler(
            (filters.ChatType.GROUPS | filters.ChatType.CHANNEL), passive_detect
        ),
        group=1,
    )
    return app


def main() -> None:
    print("\n" + "=" * 50)
    print("  Telegram Bot Listener - Auto-Detection + Poster")
    print("=" * 50)
    print("  Listening for new groups/channels and /post commands...")
    print("  Press Ctrl+C to stop\n")

    app = build_application()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
