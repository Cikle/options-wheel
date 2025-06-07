from pathlib import Path
from core.broker_client import BrokerClient
from core.execution import sell_puts, sell_calls
from core.state_manager import update_state, calculate_risk
from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER
from config.params import MAX_RISK
from logs.strategy_logger import StrategyLogger
from logs.logger_setup import setup_logger
from logs.discord_notifier import DiscordNotifier
from core.cli_args import parse_args
from core.market_hours import MarketHoursChecker, log_market_status
from core.continuous_scheduler import ContinuousScheduler

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

def test_market_hours():
    """Test market hours functionality"""
    print("Testing market hours checker...")
    print("="*50)
    
    log_market_status()
    
    checker = MarketHoursChecker()
    status = checker.get_market_status()
    
    print("\nDetailed Market Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Market hours test completed!")

def execute_strategy_once(args):
    """Execute the strategy once (extracted for use by scheduler)"""
    # Initialize loggers and notifier
    strat_logger = StrategyLogger(enabled=args.strat_log)
    logger = setup_logger(level=args.log_level, to_file=args.log_to_file)
    discord_notifier = DiscordNotifier()

    # Check if options trading is allowed
    market_checker = MarketHoursChecker()
    if not market_checker.can_trade_options():
        status = market_checker.get_market_status()
        message = f"⏰ Options trading not allowed at this time\n"
        message += f"Market Phase: {status['market_phase']}\n"
        message += f"Next Market Open: {status['next_market_open']}"
        
        logger.warning("Options trading not allowed at this time")
        log_market_status()
        
        if discord_notifier.enabled:
            discord_notifier.send_message(message, title="⏰ Market Closed", color=0xf39c12)
        
        return False  # Indicate that strategy was not executed

    strat_logger.set_fresh_start(args.fresh_start)

    SYMBOLS_FILE = Path(__file__).parent.parent / "config" / "symbol_list.txt"
    with open(SYMBOLS_FILE, 'r') as file:
        SYMBOLS = [line.strip() for line in file.readlines()]

    client = BrokerClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY, paper=IS_PAPER)

    try:
        if args.fresh_start:
            logger.info("Running in fresh start mode — liquidating all positions.")
            discord_notifier.send_startup_message(fresh_start=True, buying_power=MAX_RISK, allowed_symbols=SYMBOLS)
            client.liquidate_all_positions()
            allowed_symbols = SYMBOLS
            buying_power = MAX_RISK
        else:
            positions = client.get_positions()
            strat_logger.add_current_positions(positions)

            # Send position update to Discord
            if positions:
                positions_summary = [
                    {
                        "symbol": pos.symbol,
                        "side": pos.side.title().lower(),
                        "qty": pos.qty,
                        "purchase_price": pos.avg_entry_price,
                        "current_price": pos.current_price,
                        "pnl": pos.unrealized_pl
                    }
                    for pos in positions
                ]
                discord_notifier.send_position_update(positions_summary)

            current_risk = calculate_risk(positions)
            
            states = update_state(positions)
            strat_logger.add_state_dict(states)

            for symbol, state in states.items():
                if state["type"] == "long_shares":
                    sell_calls(client, symbol, state["price"], state["qty"], strat_logger, discord_notifier)

            allowed_symbols = list(set(SYMBOLS).difference(states.keys()))
            buying_power = MAX_RISK - current_risk

            # Send startup message for regular mode
            discord_notifier.send_startup_message(fresh_start=False, buying_power=buying_power, allowed_symbols=allowed_symbols)
        
        strat_logger.set_buying_power(buying_power)
        strat_logger.set_allowed_symbols(allowed_symbols)

        logger.info(f"Current buying power is ${buying_power}")
        
        # Track trades for summary
        trades_summary = {"puts_sold": 0, "calls_sold": 0, "total_premium": 0.0}
        
        sell_puts(client, allowed_symbols, buying_power, strat_logger, discord_notifier, trades_summary)

        # Send completion notification
        discord_notifier.send_completion_message(trades_summary)

        strat_logger.save()
        return True  # Indicate successful execution

    except Exception as e:
        logger.error(f"Error during strategy execution: {e}")
        discord_notifier.send_error_notification(str(e), "Strategy execution")
        raise

def main():
    args = parse_args()
    
    # If testing Discord, run test and exit
    if args.test_discord:
        test_discord_webhook()
        return
    
    # If testing market hours, run test and exit
    if args.test_market_hours:
        test_market_hours()
        return
    
    # If continuous mode, start the scheduler
    if args.continuous:
        logger = setup_logger(level=args.log_level, to_file=args.log_to_file)
        logger.info("Starting Options Wheel Bot in continuous 24/7 mode...")
        
        # Create and start the continuous scheduler
        scheduler = ContinuousScheduler(
            strategy_function=lambda: execute_strategy_once(args),
            check_interval_minutes=args.check_interval,
            max_runs_per_day=args.max_runs_per_day,
            discord_notifier=DiscordNotifier()
        )
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal. Shutting down...")
            scheduler.stop()
        return
    
    # Default: Execute strategy once
    execute_strategy_once(args)

if __name__ == "__main__":
    main()
