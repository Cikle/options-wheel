#!/usr/bin/env python3
"""
Complete system test for Options Wheel Bot 24/7 automation.
This script tests all components and provides setup validation.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from core.market_hours import MarketHoursChecker
        from logging.discord_notifier import DiscordNotifier
        from core.continuous_scheduler import ContinuousScheduler
        from core.cli_args import parse_args
        print("  ✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\n🔧 Testing environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️  .env file not found (you may need to create one)")
    
    # Test credential loading
    try:
        from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER
        
        if ALPACA_API_KEY and ALPACA_SECRET_KEY:
            print("  ✅ Alpaca credentials configured")
        else:
            print("  ⚠️  Alpaca credentials not configured")
            
        print(f"  📊 Paper trading: {IS_PAPER}")
        
    except Exception as e:
        print(f"  ❌ Error loading credentials: {e}")
        return False
    
    return True

def test_market_hours():
    """Test market hours functionality."""
    print("\n⏰ Testing market hours...")
    
    try:
        from core.market_hours import MarketHoursChecker
        
        checker = MarketHoursChecker()
        status = checker.get_market_status()
        
        print(f"  📅 Current time (ET): {status['current_time_et']}")
        print(f"  🏢 Market phase: {status['market_phase']}")
        print(f"  📈 Can trade options: {status['can_trade_options']}")
        
        if not status['can_trade_options']:
            print(f"  ⏭️  Next market open: {status['next_market_open']}")
        
        print("  ✅ Market hours system working")
        return True
        
    except Exception as e:
        print(f"  ❌ Market hours error: {e}")
        return False

def test_discord():
    """Test Discord integration."""
    print("\n📱 Testing Discord integration...")
    
    try:
        from logging.discord_notifier import DiscordNotifier
        
        notifier = DiscordNotifier()
        
        if notifier.enabled:
            print("  ✅ Discord notifications enabled")
            print(f"  🔗 Webhook configured: {notifier.webhook_url[:50]}...")
            
            # Test sending a message
            try:
                notifier.send_message(
                    "🧪 System test completed successfully!",
                    title="🤖 Options Wheel Bot - System Test",
                    color=0x00ff00
                )
                print("  ✅ Test message sent to Discord")
                return True
            except Exception as e:
                print(f"  ❌ Failed to send Discord message: {e}")
                return False
        else:
            print("  ⚠️  Discord notifications disabled or not configured")
            return True  # Not an error, just not configured
            
    except Exception as e:
        print(f"  ❌ Discord integration error: {e}")
        return False

def test_symbol_list():
    """Test symbol list configuration."""
    print("\n📋 Testing symbol list...")
    
    try:
        symbols_file = Path("config/symbol_list.txt")
        
        if symbols_file.exists():
            with open(symbols_file, 'r') as f:
                symbols = [line.strip() for line in f.readlines() if line.strip()]
            
            print(f"  ✅ Symbol list found with {len(symbols)} symbols")
            print(f"  📊 Symbols: {', '.join(symbols[:5])}{' ...' if len(symbols) > 5 else ''}")
            
            if len(symbols) == 0:
                print("  ⚠️  Warning: No symbols in list")
            
            return True
        else:
            print("  ❌ Symbol list file not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Symbol list error: {e}")
        return False

def test_cli_args():
    """Test CLI argument parsing."""
    print("\n🖥️  Testing CLI arguments...")
    
    try:
        from core.cli_args import parse_args
        
        # Test with no arguments (should use defaults)
        import sys
        original_argv = sys.argv.copy()
        sys.argv = ['test']  # Simulate script name only
        
        args = parse_args()
        
        # Check that new arguments exist
        required_attrs = ['continuous', 'check_interval', 'max_runs_per_day', 'test_market_hours']
        missing_attrs = [attr for attr in required_attrs if not hasattr(args, attr)]
        
        if missing_attrs:
            print(f"  ❌ Missing CLI arguments: {missing_attrs}")
            return False
        
        print("  ✅ All CLI arguments available")
        print(f"  ⚙️  Default check interval: {args.check_interval} minutes")
        print(f"  🎯 Default max runs per day: {args.max_runs_per_day}")
        
        # Restore original argv
        sys.argv = original_argv
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI arguments error: {e}")
        return False

def main():
    """Run complete system test."""
    print("🤖 Options Wheel Bot - Complete System Test")
    print("=" * 60)
    print("This script validates that your 24/7 automation setup is ready.")
    print()
    
    tests = [
        test_imports,
        test_environment,
        test_cli_args,
        test_symbol_list,
        test_market_hours,
        test_discord,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SYSTEM TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All systems go! Your bot is ready for 24/7 automation.")
        print()
        print("🚀 To start continuous mode:")
        print("   python -m scripts.run_strategy --continuous")
        print()
        print("📚 For detailed usage instructions:")
        print("   See AUTOMATION_GUIDE.md")
          # Send success notification to Discord if available
        try:
            from logging.discord_notifier import DiscordNotifier
            notifier = DiscordNotifier()
            if notifier.enabled:
                notifier.send_message(
                    f"🎉 **System Test Completed Successfully!**\n" +
                    f"✅ All {total} tests passed\n" +
                    f"🤖 Bot is ready for 24/7 automation",
                    title="🚀 Options Wheel Bot - Ready!",
                    color=0x00ff00
                )
        except:
            pass  # Don't fail the test if Discord fails
        
    else:
        failed = total - passed
        print(f"⚠️  {failed} test(s) failed. Please review the issues above.")
        print()
        print("📋 Common fixes:")
        print("   - Create .env file with your API credentials")
        print("   - Configure Discord webhook (optional)")
        print("   - Add symbols to config/symbol_list.txt")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
