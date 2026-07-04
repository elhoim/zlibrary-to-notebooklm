#!/usr/bin/env python3
"""
Z-Library Login - one-time login that saves the session state

Works similarly to `notebooklm login`
"""

import asyncio
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright is not installed")
    print("Please run: pip install playwright")
    sys.exit(1)


def zlibrary_login():
    """Log in to Z-Library and save the session"""

    config_dir = Path.home() / ".zlibrary"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.chmod(0o700)

    storage_state = config_dir / "storage_state.json"

    print("="*70)
    print("🔐 Z-Library Login")
    print("="*70)
    print("")
    print("Instructions:")
    print("  1. A browser will open automatically and visit Z-Library")
    print("  2. Complete the login manually (if required)")
    print("  3. After a successful login, return to the terminal and press ENTER")
    print("  4. The session state will be saved so you won't need to log in again")
    print("")

    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(config_dir / "browser_profile"),
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            print("📖 Visiting Z-Library...")
            page.goto("https://zh.zlib.li/", wait_until='domcontentloaded', timeout=30000)

            print("")
            print("="*70)
            print("📋 Steps:")
            print("="*70)
            print("1. Complete the login in the browser (if not already logged in)")
            print("2. Wait until you see the Z-Library home page")
            print("3. Return to the terminal and press ENTER to continue")
            print("="*70)
            print("")

            input("✅ Finished logging in? Press ENTER to save the session... ")

            # Save the session state
            browser.storage_state(path=str(storage_state))
            storage_state.chmod(0o600)

            print("")
            print("✅ Session saved!")
            print(f"📁 Location: {storage_state}")
            print("")
            print("💡 You can now run the automation script:")
            print("   python3 scripts/upload.py <Z-Library URL>")
            print("")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()


def main():
    """Main entry point"""
    zlibrary_login()


if __name__ == "__main__":
    main()
