import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--fresh-start", 
        action="store_true", 
        help="Liquidate all positions before running"
    )

    parser.add_argument(
        "--strat-log", 
        action="store_true", 
        help="Enable strategy JSON logging"
    )

    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level for consol/file logs"
    )

    parser.add_argument(
        "--log-to-file",
        action="store_true",
        help="Write logs to file instead of just printing to stdout"
    )

    parser.add_argument(
        "--test-discord",
        action="store_true",
        help="Test Discord webhook functionality and exit"
    )
    
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run in continuous 24/7 mode with market hours awareness"
    )

    parser.add_argument(
        "--check-interval",
        type=int,
        default=15,
        help="Check interval in minutes for continuous mode (default: 15)"
    )

    parser.add_argument(
        "--max-runs-per-day",
        type=int,
        default=4,
        help="Maximum strategy executions per trading day (default: 4)"
    )

    parser.add_argument(
        "--test-market-hours",
        action="store_true",
        help="Test market hours checker and exit"
    )
    
    return parser.parse_args()
