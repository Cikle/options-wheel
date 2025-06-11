import json
import requests
import logging
from datetime import datetime
from config.credentials import DISCORD_WEBHOOK_URL, DISCORD_NOTIFICATIONS_ENABLED

logger = logging.getLogger(__name__)

class DiscordNotifier:
    def __init__(self, enabled=None):
        self.enabled = enabled if enabled is not None else DISCORD_NOTIFICATIONS_ENABLED
        self.webhook_url = DISCORD_WEBHOOK_URL
        
        if self.enabled and not self.webhook_url:
            logger.warning("Discord notifications are enabled but no webhook URL is configured. Disabling Discord notifications.")
            self.enabled = False 

    def send_message(self, message, title=None, color=None):
        """
        Send a message to Discord webhook.
        
        Args:
            message (str): The message content
            title (str, optional): Title for the embed
            color (int, optional): Color for the embed (default: blue)
        """
        if not self.enabled:
            return
            
        try:
            # Default colors
            if color is None:
                color = 0x3498db  # Blue
                
            embed = {
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {
                    "text": "Options Wheel Bot"
                }
            }
            
            if title:
                embed["title"] = title
                
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Discord notification: {e}")

    def send_startup_message(self, fresh_start=False, buying_power=None, allowed_symbols=None):
        """Send a message when the bot starts running."""
        if not self.enabled:
            return
            
        mode = "🔄 Fresh Start Mode" if fresh_start else "🏃 Regular Mode"
        
        message = f"**Options Wheel Strategy Bot Started**\n\n"
        message += f"**Mode:** {mode}\n"
        
        if buying_power is not None:
            message += f"**Available Buying Power:** ${buying_power:,.2f}\n"
            
        if allowed_symbols:
            symbols_text = ", ".join(allowed_symbols[:10])  # Limit to first 10 symbols
            if len(allowed_symbols) > 10:
                symbols_text += f" (+{len(allowed_symbols) - 10} more)"
            message += f"**Trading Symbols:** {symbols_text}\n"
            
        message += f"\n*Starting strategy execution...*"
        
        self.send_message(message, title="🚀 Bot Started", color=0x00ff00)  # Green

    def send_trade_notification(self, trade_type, symbol, contract_symbol, strike, premium, expiry):
        """
        Send notification about a trade execution.
        
        Args:
            trade_type (str): 'PUT' or 'CALL'
            symbol (str): Underlying symbol
            contract_symbol (str): Full option contract symbol
            strike (float): Strike price
            premium (float): Premium collected
            expiry (str): Expiration date        """
        if not self.enabled:
            return
            
        emoji = "📉" if trade_type.upper() == "PUT" else "📈"
        action = "Sold Put" if trade_type.upper() == "PUT" else "Sold Call"
        
        message = f"**{emoji} {action} Executed**\n\n"
        message += f"**Underlying:** {symbol}\n"
        message += f"**Contract:** {contract_symbol}\n"
        message += f"**Strike:** ${strike}\n"
        message += f"**Premium Collected:** ${premium:.2f}\n"
        message += f"**Expiry:** {expiry}\n"
        
        color = 0xf39c12 if trade_type.upper() == "PUT" else 0xe74c3c  # Orange for puts, red for calls
        self.send_message(message, color=color)

    def send_position_update(self, positions_summary):
        """Send notification about current positions."""
        if not self.enabled or not positions_summary:
            return
            
        message = "**📊 Current Positions Update**\n\n"
        
        for pos in positions_summary:
            # Safely convert pnl to float for comparison
            try:
                pnl_value = float(pos.get('pnl', 0))
            except (ValueError, TypeError):
                pnl_value = 0.0
                
            pnl_emoji = "📈" if pnl_value >= 0 else "📉"
            
            # Safely convert other values to float for formatting
            try:
                purchase_price = float(pos.get('purchase_price', 0))
            except (ValueError, TypeError):
                purchase_price = 0.0
                
            try:
                current_price = float(pos.get('current_price', 0))
            except (ValueError, TypeError):
                current_price = 0.0
            
            message += f"{pnl_emoji} **{pos['symbol']}**: {pos['side']} {pos['qty']} @ ${purchase_price:.2f}\n"
            message += f"   Current: ${current_price:.2f} | P&L: ${pnl_value:.2f}\n\n"
            
        self.send_message(message, color=0x9b59b6)  # Purple

    def send_error_notification(self, error_message, context=None):
        """Send notification about errors."""
        if not self.enabled:
            return
            
        message = f"**❌ Error Occurred**\n\n"
        message += f"**Error:** {error_message}\n"
        
        if context:
            message += f"**Context:** {context}\n"
            
        self.send_message(message, color=0xe74c3c)  # Red

    def send_completion_message(self, summary):
        """Send message when strategy execution completes."""
        if not self.enabled:
            return
            
        message = "**✅ Strategy Execution Completed**\n\n"
        
        if summary.get('puts_sold'):
            message += f"**Puts Sold:** {summary['puts_sold']} contracts\n"
        if summary.get('calls_sold'):
            message += f"**Calls Sold:** {summary['calls_sold']} contracts\n"
        if summary.get('total_premium'):
            message += f"**Total Premium Collected:** ${summary['total_premium']:.2f}\n"
            
        message += f"\n*Next execution scheduled per cron job settings*"
        
        self.send_message(message, title="✅ Execution Complete", color=0x27ae60)  # Green

    def send_scheduler_notification(self, event_type, message):
        """
        Send notification about scheduler events.
        
        Args:
            event_type (str): Type of event ('startup', 'execution_start', 'execution_complete', 'shutdown')
            message (str): The message to send
        """
        if not self.enabled:
            return
            
        color_map = {
            'startup': 0x00ff00,      # Green
            'execution_start': 0xf39c12,  # Orange
            'execution_complete': 0x27ae60,  # Green
            'shutdown': 0x95a5a6      # Gray
        }
        
        title_map = {
            'startup': '🤖 Scheduler Started',
            'execution_start': '🚀 Execution Starting',
            'execution_complete': '✅ Execution Complete',
            'shutdown': '🛑 Scheduler Shutdown'
        }
        
        color = color_map.get(event_type, 0x3498db)  # Default blue
        title = title_map.get(event_type, '📢 Scheduler Update')
        
        self.send_message(message, title=title, color=color)

    def send_insufficient_funds_notification(self, symbol, required_amount, available_amount):
        """
        Send notification when there are insufficient funds for a trade.
        
        Args:
            symbol (str): The symbol that was skipped
            required_amount (float): The amount of buying power required
            available_amount (float): The amount of buying power available
        """
        if not self.enabled:
            return
            
        shortfall = required_amount - available_amount
        
        message = f"**🟠 Insufficient Funds - Continuing**\n\n"
        message += f"**Symbol:** {symbol}\n"
        message += f"**Required:** ${required_amount:,.2f}\n"
        message += f"**Available:** ${available_amount:,.2f}\n"
        message += f"**Shortfall:** ${shortfall:,.2f}\n\n"
        message += f"*Skipping {symbol} and continuing to check other symbols...*"
        
        self.send_message(message, title="⚠️ Insufficient Buying Power", color=0xf39c12)  # Orange
