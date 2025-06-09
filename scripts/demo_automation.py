#!/usr/bin/env python3
"""
Demo script to show continuous scheduler functionality without executing real trades.
This is useful for testing the 24/7 automation system.
"""

import time
import logging
from datetime import datetime
from core.market_hours import MarketHoursChecker, log_market_status
from logging.discord_notifier import DiscordNotifier

def demo_strategy_function():
    """Mock strategy function that simulates execution without real trades."""
    print(f"🎯 [DEMO] Strategy execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   📊 This would normally:")
    print("   - Check current positions")
    print("   - Analyze market conditions") 
    print("   - Execute put/call trades")
    print("   - Update position logs")
    print("   ✅ Demo execution completed!")
    time.sleep(2)  # Simulate some processing time

def main():
    print("🤖 Options Wheel Bot - 24/7 Automation Demo")
    print("="*60)
    print("This demo shows how the continuous scheduler works")
    print("WITHOUT executing any real trades.\n")
    
    # Test market hours first
    print("📊 Current Market Status:")
    log_market_status()
    print()
    
    # Initialize components
    market_checker = MarketHoursChecker()
    discord_notifier = DiscordNotifier()
    
    print("🔄 Starting demo scheduler...")
    
    # Send demo Discord notification if enabled
    if discord_notifier.enabled:
        discord_notifier.send_scheduler_notification(
            "startup",
            "🧪 **Demo Mode Started**\n" +
            "This is a demonstration of the 24/7 automation system.\n" +
            "No real trades will be executed."
        )
    
    try:
        run_count = 0
        max_demo_runs = 3  # Limit demo to 3 iterations
        
        while run_count < max_demo_runs:
            print(f"\n⏰ Demo Check #{run_count + 1}")
            
            # Check market status
            status = market_checker.get_market_status()
            can_trade = market_checker.can_trade_options()
            
            print(f"   Market Phase: {status['market_phase']}")
            print(f"   Can Trade Options: {can_trade}")
            
            if can_trade:
                print("   ✅ Market is open - executing demo strategy...")
                demo_strategy_function()
                run_count += 1
                
                if discord_notifier.enabled:
                    discord_notifier.send_scheduler_notification(
                        "execution_complete",
                        f"🧪 Demo execution #{run_count} completed"
                    )
            else:
                print(f"   ⏰ Market closed - next open: {status['next_market_open']}")
                if discord_notifier.enabled:
                    discord_notifier.send_message(
                        f"⏰ Demo check: Market closed\n" +
                        f"Next open: {status['next_market_open']}",
                        title="🧪 Demo - Market Closed",
                        color=0xf39c12
                    )
            
            if run_count < max_demo_runs:
                print("   💤 Waiting 30 seconds for next check...")
                time.sleep(30)  # Short interval for demo
    
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    
    print(f"\n✅ Demo completed! ({run_count} executions)")
    
    if discord_notifier.enabled:
        discord_notifier.send_scheduler_notification(
            "shutdown",
            f"🧪 Demo completed with {run_count} executions"
        )

if __name__ == "__main__":
    main()
