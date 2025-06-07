from pathlib import Path
from core.broker_client import BrokerClient
from core.execution import sell_puts, sell_calls
from core.state_manager import update_state, calculate_risk
from config.credentials import ALPACA_API_KEY, ALPACA_SECRET_KEY, IS_PAPER
from config.params import MAX_RISK
from logging.strategy_logger import StrategyLogger
from logging.logger_setup import setup_logger
from logging.discord_notifier import DiscordNotifier
from core.cli_args import parse_args

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

def main():
    args = parse_args()
    
    # If testing Discord, run test and exit
    if args.test_discord:
        test_discord_webhook()
        return
    
    # Initialize loggers and notifier
    strat_logger = StrategyLogger(enabled=args.strat_log)  # custom JSON logger used to persist strategy-specific state (e.g. trades, symbols, PnL).
    logger = setup_logger(level=args.log_level, to_file=args.log_to_file) # standard Python logger used for general runtime messages, debugging, and error reporting.
    discord_notifier = DiscordNotifier()  # Discord webhook notifier

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

    except Exception as e:
        logger.error(f"Error during strategy execution: {e}")
        discord_notifier.send_error_notification(str(e), "Strategy execution")
        raise

if __name__ == "__main__":
    main()
