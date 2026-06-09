#!/usr/bin/env python3
"""
Command-Line Interface for Telegram Bot Poster
Provides interactive menu for managing chats and sending messages.
"""
import asyncio
import sys
import os
from bot_core import TelegramBotPoster
from config import BOT_TOKEN


def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header():
    print("\n" + "=" * 60)
    print("       TELEGRAM BOT POSTER - Command Line Interface")
    print("=" * 60)


def print_menu():
    print("\n┌─────────────────────────────────────────────┐")
    print("│              MAIN MENU                       │")
    print("├─────────────────────────────────────────────┤")
    print("│  1. Test Bot Connection                     │")
    print("│  2. Auto-Detect Chats                       │")
    print("│  3. Add Chat by ID                          │")
    print("│  4. Add Chat Manually                       │")
    print("│  5. View Saved Chats                        │")
    print("│  6. Remove a Chat                           │")
    print("│  7. Send Message to Specific Chat           │")
    print("│  8. Send Message to Multiple Chats          │")
    print("│  9. Send Message to All Saved Chats         │")
    print("│ 10. Get Chat Info by ID                     │")
    print("│  0. Exit                                    │")
    print("└─────────────────────────────────────────────┘")


def display_chats(chats):
    """Display chats in a formatted table."""
    if not chats:
        print("\n  ⚠️  No chats found.")
        return

    print(f"\n  {'#':<4} {'ID':<15} {'Title':<25} {'Type':<12} {'Username':<15}")
    print("  " + "-" * 75)
    for i, (chat_id, info) in enumerate(chats.items(), 1):
        title = info.get('title', 'Unknown')[:24]
        chat_type = info.get('type', 'unknown')
        username = info.get('username', '')[:14]
        auto = "🔍" if info.get('auto_detected') else "✋"
        print(f"  {i:<4} {chat_id:<15} {title:<25} {chat_type:<12} @{username:<14} {auto}")

    print(f"\n  Total: {len(chats)} chat(s) | 🔍 = Auto-detected | ✋ = Manually added")


async def main():
    """Main CLI loop."""
    bot = TelegramBotPoster()

    print_header()
    print(f"\n  Bot Token: {BOT_TOKEN[:20]}...")

    # Test connection on start
    print("\n  Testing connection...")
    result = await bot.test_connection()
    if result["success"]:
        print(f"  ✅ Connected as @{result['bot_username']} (ID: {result['bot_id']})")
    else:
        print(f"  ❌ Connection failed: {result['error']}")
        print("  Please check your bot token in config.py")
        sys.exit(1)

    while True:
        print_menu()
        choice = input("\n  Enter your choice: ").strip()

        if choice == "1":
            # Test Connection
            print("\n  Testing bot connection...")
            result = await bot.test_connection()
            if result["success"]:
                print(f"  ✅ Bot is online: @{result['bot_username']}")
                info = await bot.get_bot_info()
                if info:
                    print(f"  📋 Bot ID: {info['id']}")
                    print(f"  📋 Name: {info['first_name']}")
                    print(f"  📋 Can join groups: {info['can_join_groups']}")
                    print(f"  📋 Can read messages: {info['can_read_all_group_messages']}")
            else:
                print(f"  ❌ Error: {result['error']}")

        elif choice == "2":
            # Auto-Detect Chats
            print("\n  🔍 Auto-detecting chats from recent updates...")
            print("  (Make sure the bot has been added to groups/channels)")
            detected = await bot.auto_detect_chats()
            if detected:
                print(f"\n  ✅ Detected {len(detected)} new chat(s):")
                display_chats(detected)
            else:
                print("\n  ℹ️  No new chats detected.")
                print("  Tips:")
                print("  - Add the bot to a group/channel as admin")
                print("  - Send a message in the group after adding the bot")
                print("  - Use /start in a group with the bot")

            # Show all saved
            all_chats = bot.get_saved_chats()
            if all_chats:
                print("\n  📋 All saved chats:")
                display_chats(all_chats)

        elif choice == "3":
            # Add Chat by ID
            chat_id = input("\n  Enter Chat ID (e.g., -1001234567890): ").strip()
            if not chat_id:
                print("  ❌ No ID provided.")
                continue

            print(f"  🔍 Looking up chat {chat_id}...")
            chat_info = await bot.add_chat_by_id(chat_id)
            if chat_info:
                print(f"  ✅ Added: {chat_info['title']} ({chat_info['type']})")
            else:
                print("  ❌ Could not find chat. Make sure the bot is a member.")
                add_anyway = input("  Add manually anyway? (y/n): ").strip().lower()
                if add_anyway == 'y':
                    title = input("  Enter chat title (optional): ").strip()
                    bot.add_chat_manually(chat_id, title)
                    print("  ✅ Chat added manually.")

        elif choice == "4":
            # Add Chat Manually
            chat_id = input("\n  Enter Chat ID: ").strip()
            title = input("  Enter Chat Title: ").strip()
            chat_type = input("  Enter Type (group/supergroup/channel): ").strip() or "unknown"

            if chat_id:
                bot.add_chat_manually(chat_id, title, chat_type)
                print(f"  ✅ Manually added: {title or chat_id}")
            else:
                print("  ❌ Chat ID is required.")

        elif choice == "5":
            # View Saved Chats
            chats = bot.get_saved_chats()
            print("\n  📋 Saved Chats:")
            display_chats(chats)

        elif choice == "6":
            # Remove a Chat
            chats = bot.get_saved_chats()
            if not chats:
                print("\n  ⚠️  No saved chats to remove.")
                continue

            display_chats(chats)
            chat_id = input("\n  Enter Chat ID to remove: ").strip()
            removed = bot.remove_chat(chat_id)
            if removed:
                print(f"  ✅ Removed: {removed['title']}")
            else:
                print("  ❌ Chat not found in saved list.")

        elif choice == "7":
            # Send Message to Specific Chat
            chats = bot.get_saved_chats()
            if chats:
                print("\n  📋 Available chats:")
                display_chats(chats)

            chat_id = input("\n  Enter Chat ID (or # from list): ").strip()

            # Allow selection by number
            if chat_id.isdigit() and int(chat_id) <= len(chats) and int(chat_id) > 0:
                chat_id = list(chats.keys())[int(chat_id) - 1]

            message = input("  Enter message: ").strip()
            if not message:
                print("  ❌ Message cannot be empty.")
                continue

            parse_mode = input("  Parse mode (HTML/Markdown/none): ").strip() or None
            if parse_mode and parse_mode.lower() == 'none':
                parse_mode = None

            print(f"\n  📤 Sending to {chat_id}...")
            result = await bot.send_message(chat_id, message, parse_mode=parse_mode)
            if result["success"]:
                print(f"  ✅ Message sent! (ID: {result['message_id']})")
            else:
                print(f"  ❌ Failed: {result['error']}")

        elif choice == "8":
            # Send to Multiple Chats
            chats = bot.get_saved_chats()
            if chats:
                print("\n  📋 Available chats:")
                display_chats(chats)

            ids_input = input("\n  Enter Chat IDs (comma-separated, or # from list): ").strip()
            chat_ids = []
            for item in ids_input.split(","):
                item = item.strip()
                if item.isdigit() and int(item) <= len(chats) and int(item) > 0:
                    chat_ids.append(list(chats.keys())[int(item) - 1])
                else:
                    chat_ids.append(item)

            message = input("  Enter message: ").strip()
            if not message:
                print("  ❌ Message cannot be empty.")
                continue

            parse_mode = input("  Parse mode (HTML/Markdown/none): ").strip() or None
            if parse_mode and parse_mode.lower() == 'none':
                parse_mode = None

            print(f"\n  📤 Sending to {len(chat_ids)} chat(s)...")
            results = await bot.send_to_multiple(chat_ids, message, parse_mode=parse_mode)
            for cid, res in results.items():
                status = "✅" if res["success"] else "❌"
                detail = f"ID: {res.get('message_id', 'N/A')}" if res["success"] else res.get("error", "Unknown error")
                print(f"  {status} {cid}: {detail}")

        elif choice == "9":
            # Send to All Saved Chats
            chats = bot.get_saved_chats()
            if not chats:
                print("\n  ⚠️  No saved chats. Add some first.")
                continue

            print(f"\n  📋 Will send to {len(chats)} chat(s):")
            display_chats(chats)

            confirm = input("\n  Confirm send to all? (y/n): ").strip().lower()
            if confirm != 'y':
                print("  Cancelled.")
                continue

            message = input("  Enter message: ").strip()
            if not message:
                print("  ❌ Message cannot be empty.")
                continue

            parse_mode = input("  Parse mode (HTML/Markdown/none): ").strip() or None
            if parse_mode and parse_mode.lower() == 'none':
                parse_mode = None

            print("\n  📤 Broadcasting to all saved chats...")
            results = await bot.send_to_all_saved(message, parse_mode=parse_mode)
            success_count = sum(1 for r in results.values() if r["success"])
            print(f"\n  📊 Results: {success_count}/{len(results)} sent successfully")
            for cid, res in results.items():
                status = "✅" if res["success"] else "❌"
                title = chats.get(cid, {}).get('title', cid)
                print(f"  {status} {title}")

        elif choice == "10":
            # Get Chat Info
            chat_id = input("\n  Enter Chat ID: ").strip()
            if not chat_id:
                print("  ❌ No ID provided.")
                continue

            print(f"  🔍 Looking up chat {chat_id}...")
            info = await bot.get_chat_info(chat_id)
            if info:
                print("\n  📋 Chat Information:")
                print(f"  ├─ ID: {info['id']}")
                print(f"  ├─ Title: {info['title']}")
                print(f"  ├─ Type: {info['type']}")
                print(f"  ├─ Username: @{info['username']}" if info['username'] else "  ├─ Username: N/A")
                print(f"  ├─ Description: {info['description'][:50]}" if info['description'] else "  ├─ Description: N/A")
                print(f"  └─ Members: {info['member_count']}" if info['member_count'] else "  └─ Members: N/A")
            else:
                print("  ❌ Could not retrieve chat info.")

        elif choice == "0":
            print("\n  👋 Goodbye!")
            sys.exit(0)

        else:
            print("\n  ❌ Invalid choice. Please try again.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
