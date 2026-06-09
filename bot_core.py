"""
Core Telegram Bot Module
Handles auto-detection of chats, sending messages, and chat management.
"""
import asyncio
import logging
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, Forbidden, BadRequest
from telegram.constants import ChatType
from config import BOT_TOKEN, configured_buttons, load_saved_chats, save_chats

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def build_link_keyboard():
    """Inline keyboard of the configured link buttons (one per row).

    Returns ``None`` when no button URLs are configured.
    """
    rows = [
        [InlineKeyboardButton(label, url=url)] for label, url in configured_buttons()
    ]
    return InlineKeyboardMarkup(rows) if rows else None


class TelegramBotPoster:
    """Main bot class for posting messages to groups and channels."""

    def __init__(self, token=None):
        self.token = token or BOT_TOKEN
        self.saved_chats = load_saved_chats()

    def _get_bot(self):
        """Create a fresh Bot instance to avoid event loop issues."""
        return Bot(token=self.token)

    async def get_bot_info(self):
        """Get bot information."""
        try:
            bot = self._get_bot()
            me = await bot.get_me()
            return {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "can_join_groups": me.can_join_groups,
                "can_read_all_group_messages": me.can_read_all_group_messages,
            }
        except TelegramError as e:
            logger.error(f"Error getting bot info: {e}")
            return None

    async def auto_detect_chats(self):
        """
        Auto-detect chats by checking updates.
        The bot discovers groups/channels when it receives messages or is added.
        This fetches recent updates to find chats the bot is part of.
        """
        detected_chats = {}

        try:
            bot = self._get_bot()
            # Get recent updates to discover chats
            updates = await bot.get_updates(limit=100, timeout=5)

            for update in updates:
                chat = None

                if update.message and update.message.chat:
                    chat = update.message.chat
                elif update.channel_post and update.channel_post.chat:
                    chat = update.channel_post.chat
                elif update.my_chat_member:
                    chat = update.my_chat_member.chat
                elif update.edited_message and update.edited_message.chat:
                    chat = update.edited_message.chat

                if chat and chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
                    chat_id = str(chat.id)
                    if chat_id not in detected_chats:
                        chat_info = {
                            "id": chat.id,
                            "title": chat.title or "Unknown",
                            "type": chat.type,
                            "username": chat.username or "",
                            "detected_at": datetime.now().isoformat(),
                            "auto_detected": True
                        }
                        detected_chats[chat_id] = chat_info

            # Merge with saved chats
            for chat_id, chat_info in detected_chats.items():
                if chat_id not in self.saved_chats:
                    self.saved_chats[chat_id] = chat_info

            # Save updated chats
            save_chats(self.saved_chats)
            logger.info(f"Auto-detected {len(detected_chats)} chat(s)")

        except TelegramError as e:
            logger.error(f"Error during auto-detection: {e}")

        return detected_chats

    async def get_chat_info(self, chat_id):
        """Get information about a specific chat by ID."""
        try:
            bot = self._get_bot()
            chat = await bot.get_chat(chat_id=int(chat_id))
            chat_info = {
                "id": chat.id,
                "title": chat.title or chat.first_name or "Unknown",
                "type": chat.type,
                "username": chat.username or "",
                "description": chat.description or "",
                "member_count": getattr(chat, 'member_count', None),
                "detected_at": datetime.now().isoformat(),
                "auto_detected": False
            }
            return chat_info
        except TelegramError as e:
            logger.error(f"Error getting chat info for {chat_id}: {e}")
            return None

    async def add_chat_by_id(self, chat_id):
        """Add a chat by its ID to the saved list."""
        chat_info = await self.get_chat_info(chat_id)
        if chat_info:
            self.saved_chats[str(chat_id)] = chat_info
            save_chats(self.saved_chats)
            return chat_info
        return None

    def add_chat_manually(self, chat_id, title="", chat_type="unknown"):
        """Add a chat manually without verification."""
        chat_info = {
            "id": int(chat_id),
            "title": title or f"Chat {chat_id}",
            "type": chat_type,
            "username": "",
            "detected_at": datetime.now().isoformat(),
            "auto_detected": False,
            "manually_added": True
        }
        self.saved_chats[str(chat_id)] = chat_info
        save_chats(self.saved_chats)
        return chat_info

    def remove_chat(self, chat_id):
        """Remove a chat from the saved list."""
        chat_id_str = str(chat_id)
        if chat_id_str in self.saved_chats:
            removed = self.saved_chats.pop(chat_id_str)
            save_chats(self.saved_chats)
            return removed
        return None

    def get_saved_chats(self):
        """Get all saved chats."""
        self.saved_chats = load_saved_chats()
        return self.saved_chats

    async def send_message(self, chat_id, text, parse_mode=None,
                           disable_notification=False, include_buttons=True):
        """Send a text message to a specific chat, with link buttons attached."""
        try:
            bot = self._get_bot()
            reply_markup = build_link_keyboard() if include_buttons else None
            message = await bot.send_message(
                chat_id=int(chat_id),
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                reply_markup=reply_markup
            )
            logger.info(f"Message sent to {chat_id}: {text[:50]}...")
            return {
                "success": True,
                "message_id": message.message_id,
                "chat_id": chat_id,
                "date": message.date.isoformat() if message.date else None
            }
        except Forbidden as e:
            logger.error(f"Forbidden: Bot not admin or blocked in {chat_id}: {e}")
            return {"success": False, "error": f"Bot is not admin or is blocked: {e}"}
        except BadRequest as e:
            logger.error(f"Bad request for {chat_id}: {e}")
            return {"success": False, "error": f"Bad request: {e}"}
        except TelegramError as e:
            logger.error(f"Error sending to {chat_id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_to_multiple(self, chat_ids, text, parse_mode=None,
                               disable_notification=False, include_buttons=True):
        """Send a message to multiple chats."""
        results = {}
        for chat_id in chat_ids:
            result = await self.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                include_buttons=include_buttons
            )
            results[str(chat_id)] = result
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        return results

    async def send_to_all_saved(self, text, parse_mode=None,
                                disable_notification=False, include_buttons=True):
        """Send a message to all saved chats."""
        self.saved_chats = load_saved_chats()
        chat_ids = [info["id"] for info in self.saved_chats.values()]
        return await self.send_to_multiple(
            chat_ids, text, parse_mode, disable_notification, include_buttons
        )

    async def test_connection(self):
        """Test the bot connection."""
        try:
            bot = self._get_bot()
            me = await bot.get_me()
            return {"success": True, "bot_username": me.username, "bot_id": me.id}
        except TelegramError as e:
            return {"success": False, "error": str(e)}


def run_async(coro):
    """Helper to run async functions synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)
