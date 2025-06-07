# Test script for Discord webhook functionality
# Run this script to test if your Discord webhook is working correctly

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logs.discord_notifier import DiscordNotifier

def test_discord_webhook():
    """Test Discord webhook functionality"""
    print("Testing Discord webhook functionality...")
    
    # Initialize the Discord notifier
    notifier = DiscordNotifier()
    
    if not notifier.enabled:
        print("❌ Discord notifications are disabled or not configured.")
        print("To enable Discord notifications:")
        print("1. Add DISCORD_WEBHOOK_URL to your .env file")
        print("2. Set DISCORD_NOTIFICATIONS_ENABLED=true in your .env file")
        return False
    
    print("✅ Discord notifications are enabled")
    print(f"📡 Webhook URL configured: {notifier.webhook_url[:50]}...")
    
    try:
        # Test startup message
        print("📤 Sending test startup message...")
        notifier.send_startup_message(
            fresh_start=True, 
            buying_power=100000, 
            allowed_symbols=["AAPL", "NVDA", "TSLA"]
        )
        
        # Test trade notification
        print("📤 Sending test trade notification...")
        notifier.send_trade_notification(
            trade_type="PUT",
            symbol="AAPL",
            contract_symbol="AAPL250620P00200000",
            strike=200.0,
            premium=5.50,
            expiry="14 days"
        )
        
        # Test completion message
        print("📤 Sending test completion message...")
        notifier.send_completion_message({
            "puts_sold": 3,
            "calls_sold": 1,
            "total_premium": 850.00
        })
        
        print("✅ All test messages sent successfully!")
        print("📱 Check your Discord channel to see if the messages appeared.")
        return True
        
    except Exception as e:
        print(f"❌ Error sending Discord messages: {e}")
        return False

if __name__ == "__main__":
    test_discord_webhook()
