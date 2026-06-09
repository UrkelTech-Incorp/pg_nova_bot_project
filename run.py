#!/usr/bin/env python3
"""
Main Launcher for Telegram Bot Poster
Choose between CLI, Web Dashboard, or Listener mode.
"""
import sys
import os
import subprocess
import argparse


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║           TELEGRAM BOT POSTER                            ║
║           Post messages to groups & channels             ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Modes:                                                  ║
║    cli        - Interactive command-line interface        ║
║    web        - Web-based dashboard (localhost:5000)      ║
║    listener   - Background auto-detection listener       ║
║    all        - Run web dashboard + listener together     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(description="Telegram Bot Poster")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["cli", "web", "listener", "all"],
        help="Run mode: cli, web, listener, or all"
    )
    parser.add_argument(
        "--port", type=int, default=5000,
        help="Port for web dashboard (default: 5000)"
    )

    args = parser.parse_args()

    if not args.mode:
        print_banner()
        print("  Select a mode:")
        print("  1. CLI (Command Line Interface)")
        print("  2. Web Dashboard")
        print("  3. Listener (Auto-detect bot)")
        print("  4. Web + Listener (recommended)")
        print()

        choice = input("  Enter choice (1-4): ").strip()
        mode_map = {"1": "cli", "2": "web", "3": "listener", "4": "all"}
        args.mode = mode_map.get(choice)

        if not args.mode:
            print("  Invalid choice.")
            sys.exit(1)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    py = sys.executable

    if args.mode == "cli":
        subprocess.run([py, os.path.join(script_dir, "cli.py")], cwd=script_dir)

    elif args.mode == "web":
        os.environ["WEB_PORT"] = str(args.port)
        subprocess.run([py, os.path.join(script_dir, "web_dashboard.py")], cwd=script_dir)

    elif args.mode == "listener":
        subprocess.run([py, os.path.join(script_dir, "listener.py")], cwd=script_dir)

    elif args.mode == "all":
        print("\n  Starting Web Dashboard + Listener...")
        print(f"  Web Dashboard: http://localhost:{args.port}")
        print("  Listener: Running in background")
        print("  Press Ctrl+C to stop both\n")

        # Start listener in background
        listener_proc = subprocess.Popen(
            [sys.executable, os.path.join(script_dir, "listener.py")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            # Start web dashboard in foreground
            subprocess.run(
                [sys.executable, os.path.join(script_dir, "web_dashboard.py")],
                cwd=script_dir,
            )
        finally:
            listener_proc.terminate()
            print("\n  Stopped all services.")


if __name__ == "__main__":
    main()
