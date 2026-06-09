#!/usr/bin/env python3
"""
Web Dashboard for Telegram Bot Poster
Flask-based web interface for managing chats and sending messages.
"""
import asyncio
import logging
from flask import Flask, render_template, request, jsonify
from bot_core import TelegramBotPoster
from config import (
    BUTTON_DEFS,
    WEB_HOST,
    WEB_PORT,
    load_links,
    save_links,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = TelegramBotPoster()


def run_async_task(coro):
    """Run an async coroutine in a new event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


# ==================== WEB ROUTES ====================

@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/api/bot-info", methods=["GET"])
def api_bot_info():
    """Get bot information."""
    try:
        result = run_async_task(bot.test_connection())
        if result["success"]:
            info = run_async_task(bot.get_bot_info())
            return jsonify({"success": True, "data": info})
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/auto-detect", methods=["POST"])
def api_auto_detect():
    """Auto-detect chats."""
    try:
        detected = run_async_task(bot.auto_detect_chats())
        all_chats = bot.get_saved_chats()
        return jsonify({
            "success": True,
            "detected_count": len(detected),
            "detected": detected,
            "all_chats": all_chats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/chats", methods=["GET"])
def api_get_chats():
    """Get all saved chats."""
    try:
        chats = bot.get_saved_chats()
        return jsonify({"success": True, "chats": chats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/chats/add", methods=["POST"])
def api_add_chat():
    """Add a chat by ID."""
    data = request.json
    chat_id = data.get("chat_id")
    if not chat_id:
        return jsonify({"success": False, "error": "Chat ID is required"})

    try:
        chat_info = run_async_task(bot.add_chat_by_id(chat_id))
        if chat_info:
            return jsonify({"success": True, "chat": chat_info})
        else:
            return jsonify({"success": False, "error": "Could not find chat. Make sure bot is a member."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/chats/add-manual", methods=["POST"])
def api_add_chat_manual():
    """Add a chat manually."""
    data = request.json
    chat_id = data.get("chat_id")
    title = data.get("title", "")
    chat_type = data.get("type", "unknown")

    if not chat_id:
        return jsonify({"success": False, "error": "Chat ID is required"})

    try:
        chat_info = bot.add_chat_manually(chat_id, title, chat_type)
        return jsonify({"success": True, "chat": chat_info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/chats/remove", methods=["POST"])
def api_remove_chat():
    """Remove a chat."""
    data = request.json
    chat_id = data.get("chat_id")
    if not chat_id:
        return jsonify({"success": False, "error": "Chat ID is required"})

    try:
        removed = bot.remove_chat(chat_id)
        if removed:
            return jsonify({"success": True, "removed": removed})
        return jsonify({"success": False, "error": "Chat not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/chat-info/<chat_id>", methods=["GET"])
def api_chat_info(chat_id):
    """Get info about a specific chat."""
    try:
        info = run_async_task(bot.get_chat_info(chat_id))
        if info:
            return jsonify({"success": True, "chat": info})
        return jsonify({"success": False, "error": "Could not get chat info"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/send", methods=["POST"])
def api_send_message():
    """Send a message to one or more chats."""
    data = request.json
    chat_ids = data.get("chat_ids", [])
    message = data.get("message", "")
    parse_mode = data.get("parse_mode")
    disable_notification = data.get("disable_notification", False)
    include_buttons = data.get("include_buttons", True)

    if not chat_ids:
        return jsonify({"success": False, "error": "At least one chat ID is required"})
    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty"})

    if parse_mode == "none" or parse_mode == "":
        parse_mode = None

    try:
        if len(chat_ids) == 1:
            result = run_async_task(bot.send_message(
                chat_ids[0], message, parse_mode=parse_mode,
                disable_notification=disable_notification,
                include_buttons=include_buttons
            ))
            return jsonify({"success": True, "results": {str(chat_ids[0]): result}})
        else:
            results = run_async_task(bot.send_to_multiple(
                chat_ids, message, parse_mode=parse_mode,
                disable_notification=disable_notification,
                include_buttons=include_buttons
            ))
            return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/send-all", methods=["POST"])
def api_send_all():
    """Send a message to all saved chats."""
    data = request.json
    message = data.get("message", "")
    parse_mode = data.get("parse_mode")
    disable_notification = data.get("disable_notification", False)
    include_buttons = data.get("include_buttons", True)

    if not message:
        return jsonify({"success": False, "error": "Message cannot be empty"})

    if parse_mode == "none" or parse_mode == "":
        parse_mode = None

    try:
        results = run_async_task(bot.send_to_all_saved(
            message, parse_mode=parse_mode,
            disable_notification=disable_notification,
            include_buttons=include_buttons
        ))
        success_count = sum(1 for r in results.values() if r.get("success"))
        return jsonify({
            "success": True,
            "results": results,
            "summary": {
                "total": len(results),
                "success": success_count,
                "failed": len(results) - success_count
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/links", methods=["GET"])
def api_get_links():
    """Return the configured link-button URLs plus their labels."""
    links = load_links()
    fields = [
        {"key": key, "label": label, "url": links.get(key, "")}
        for key, label, _ in BUTTON_DEFS
    ]
    return jsonify({"success": True, "links": links, "fields": fields})


@app.route("/api/links", methods=["POST"])
def api_save_links():
    """Save the link-button URLs."""
    data = request.json or {}
    try:
        saved = save_links(data)
        return jsonify({"success": True, "links": saved})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Telegram Bot Poster - Web Dashboard")
    print("=" * 50)

    # Test connection
    result = run_async_task(bot.test_connection())
    if result["success"]:
        print(f"  ✅ Bot connected: @{result['bot_username']}")
    else:
        print(f"  ❌ Bot connection failed: {result['error']}")

    print(f"\n  🌐 Dashboard: http://localhost:{WEB_PORT}")
    print("  Press Ctrl+C to stop\n")

    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)
