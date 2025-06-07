#!/usr/bin/env python3
"""
Quick Start Script for 24/7 Options Wheel Bot
This script helps users start their fully automated bot with recommended settings.
"""

import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print welcome banner."""
    print("🤖 Options Wheel Bot - Quick Start")
    print("=" * 50)
    print("Starting your 24/7 automated options wheel bot...")
    print()

def check_setup():
    """Quick setup validation."""
    print("🔍 Checking setup...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your credentials.")
        print("See FULLY_AUTOMATED_GUIDE.md for setup instructions.")
        return False
    
    # Check symbol list
    symbols_file = Path("config/symbol_list.txt")
    if not symbols_file.exists():
        print("❌ Symbol list not found!")
        print("Please create config/symbol_list.txt with your target stocks.")
        return False
    
    print("✅ Basic setup validated")
    return True

def get_user_preferences():
    """Get user preferences for automation."""
    print("\n⚙️ Configuration Options:")
    print()
    
    print("How aggressive do you want the bot to be?")
    print("1. 🐌 Conservative (1 execution per day, check hourly)")
    print("2. 📊 Balanced (2 executions per day, check every 30 min)")  
    print("3. 🚀 Active (4 executions per day, check every 15 min)")
    print("4. 🔧 Custom settings")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            return {"max_runs": 1, "interval": 60, "name": "Conservative"}
        elif choice == "2":
            return {"max_runs": 2, "interval": 30, "name": "Balanced"}
        elif choice == "3":
            return {"max_runs": 4, "interval": 15, "name": "Active"}
        elif choice == "4":
            max_runs = int(input("Max executions per day (1-10): "))
            interval = int(input("Check interval in minutes (15-120): "))
            return {"max_runs": max_runs, "interval": interval, "name": "Custom"}
        else:
            print("Please enter 1, 2, 3, or 4")

def confirm_start(settings):
    """Confirm before starting."""
    print(f"\n🎯 Ready to start with {settings['name']} settings:")
    print(f"   📊 Max executions per day: {settings['max_runs']}")
    print(f"   ⏰ Check interval: {settings['interval']} minutes")
    print("   📱 Discord notifications: Enabled")
    print("   📝 Strategy logging: Enabled")
    print("   📄 File logging: Enabled")
    print()
    print("⚠️  IMPORTANT: Make sure you're using paper trading first!")
    print("   (IS_PAPER=true in your .env file)")
    print()
    
    confirm = input("Start the bot now? (y/N): ").strip().lower()
    return confirm in ['y', 'yes']

def start_bot(settings):
    """Start the bot with given settings."""
    print(f"\n🚀 Starting 24/7 Options Wheel Bot...")
    print("Press Ctrl+C to stop the bot at any time.")
    print()
    
    # Build command
    cmd = [
        sys.executable, "-m", "scripts.run_strategy",
        "--continuous",
        "--strat-log",
        "--log-to-file",
        "--log-level", "INFO",
        "--max-runs-per-day", str(settings['max_runs']),
        "--check-interval", str(settings['interval'])
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Start the bot
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Bot failed to start: {e}")
        return False
    
    return True

def main():
    """Main quick start function."""
    print_banner()
    
    # Check basic setup
    if not check_setup():
        print("\n📚 For setup help, see: FULLY_AUTOMATED_GUIDE.md")
        return 1
    
    # Get user preferences
    settings = get_user_preferences()
    
    # Confirm and start
    if confirm_start(settings):
        if start_bot(settings):
            print("\n✅ Bot session completed successfully!")
        else:
            print("\n❌ Bot failed to start properly")
            return 1
    else:
        print("\n⏹️ Startup cancelled by user")
    
    print("\n📚 For more options, see: FULLY_AUTOMATED_GUIDE.md")
    return 0

if __name__ == "__main__":
    sys.exit(main())
