from dotenv import load_dotenv
import os

load_dotenv(override=True)  # Load from .env file in root

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
IS_PAPER = os.getenv("IS_PAPER", "true").lower() == "true"

# Discord webhook settings
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_NOTIFICATIONS_ENABLED = os.getenv("DISCORD_NOTIFICATIONS_ENABLED", "false").lower() == "true"
