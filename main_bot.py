"""Telegram poster bot.

Features
--------
* Auto-detects every group/channel the bot is added to and remembers its id.
* Lists detected chats (/chats) and reports the current chat id (/id).
* Posts a message to a chat you pick, to a chat id you type, or to all chats,
  with inline link buttons (channel, website, donations, cam room, contact)
  attached to every post.

Configure it via environment variables (see ``config.py`` / ``.env.example``).
"""
import functools
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
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

import db
from config import BOT_TOKEN, OWNER_ID, configured_buttons

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states for the /post flow.
CHOOSE_CHAT, ENTER_ID, ENTER_TEXT = range(3)

# Member statuses that mean the bot is currently inside a chat.
_PRESENT_STATUSES = {"member", "administrator", "creator", "restricted"}
_GROUPISH = {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def build_link_keyboard() -> InlineKeyboardMarkup | None:
    """Inline keyboard of the configured link buttons (one per row)."""
    buttons = [
        [InlineKeyboardButton(label, url=url)] for label, url in configured_buttons()
    ]
    return InlineKeyboardMarkup(buttons) if buttons else None


def _remember_chat(chat) -> None:
    """Persist a group/supergroup/channel chat."""
    if chat is None or chat.type not in _GROUPISH:
        return
    title = chat.title or chat.full_name or str(chat.id)
    db.upsert_chat(chat.id, title, chat.type, chat.username)


def _chat_label(chat: db.Chat) -> str:
    icon = "📣" if chat.chat_type == ChatType.CHANNEL else "👥"
    return f"{icon} {chat.title}"


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
                await update.effective_message.reply_text(
                    "Sorry, this is a private bot."
                )
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
    new_status = result.new_chat_member.status
    chat = result.chat
    if new_status in _PRESENT_STATUSES:
        _remember_chat(chat)
        logger.info("Detected chat %s (%s)", chat.id, chat.title)
    else:
        db.remove_chat(chat.id)
        logger.info("Removed chat %s (%s)", chat.id, chat.title)


async def passive_detect(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remember any group/channel we see activity in (catches pre-existing ones)."""
    _remember_chat(update.effective_chat)


# --------------------------------------------------------------------------- #
# Basic commands
# --------------------------------------------------------------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_html(
        f"Hi {user.mention_html()}! I post messages to your groups and channels.\n\n"
        "Add me to a channel/group <b>as an admin</b> and I'll detect it "
        "automatically.\n\n"
        "Commands:\n"
        "/post – post a message (pick a chat or type an id)\n"
        "/chats – list the chats I've detected\n"
        "/id – show the current chat's id\n"
        "/whoami – show your user id\n"
        "/cancel – cancel the current action"
    )


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.effective_message.reply_text(f"Your user id is: {user.id}")


async def chat_id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    await update.effective_message.reply_text(
        f"This chat id is: {chat.id}\nType: {chat.type}"
    )


@restricted
async def list_chats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chats = db.list_chats()
    if not chats:
        await update.effective_message.reply_text(
            "I haven't detected any chats yet. Add me to a group or channel "
            "as an admin first."
        )
        return
    lines = ["Detected chats:\n"]
    for c in chats:
        handle = f" (@{c.username})" if c.username else ""
        lines.append(f"{_chat_label(c)}{handle}\n   id: {c.chat_id}")
    await update.effective_message.reply_text("\n".join(lines))


# --------------------------------------------------------------------------- #
# /post conversation
# --------------------------------------------------------------------------- #
@restricted
async def post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chats = db.list_chats()
    keyboard = [
        [InlineKeyboardButton(_chat_label(c), callback_data=f"chat:{c.chat_id}")]
        for c in chats
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
        "Where should I post?\nPick a chat below"
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
        await query.edit_message_text(
            "Send me the chat id (e.g. -1001234567890)."
        )
        return ENTER_ID

    if data == "all":
        context.user_data["targets"] = [c.chat_id for c in db.list_chats()]
        label = "all detected chats"
    else:
        context.user_data["targets"] = [int(data)]
        chat = db.get_chat(int(data))
        label = _chat_label(chat) if chat else str(data)

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
        except Exception as exc:  # noqa: BLE001 - report any send failure to the user
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


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

    db.init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    post_conv = ConversationHandler(
        entry_points=[CommandHandler("post", post_start)],
        states={
            CHOOSE_CHAT: [CallbackQueryHandler(choose_chat, pattern=r"^chat:")],
            ENTER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_id)
            ],
            ENTER_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_text)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("id", chat_id_cmd))
    app.add_handler(CommandHandler("chats", list_chats_cmd))
    app.add_handler(post_conv)

    # Auto-detect: membership changes + passive activity in groups/channels.
    app.add_handler(ChatMemberHandler(track_membership, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(
        MessageHandler(
            (filters.ChatType.GROUPS | filters.ChatType.CHANNEL), passive_detect
        ),
        group=1,
    )
    return app


def main() -> None:
    app = build_application()
    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
