"""
Strategy logging utilities for tracking trades and performance.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class StrategyLogger:
    """
    Logs strategy execution details to JSON files for analysis.
    """
    
    def __init__(self, enabled=True):
        """
        Initialize the strategy logger.
        
        Args:
            enabled (bool): Whether to enable logging
        """
        self.enabled = enabled
        self.data = {}
        self.log_file = None
        
        if self.enabled:
            self._initialize_log()
    
    def _initialize_log(self):
        """Initialize the log file and data structure."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = logs_dir / f"strategy_log_{timestamp}.json"
        
        # Initialize data structure
        self.data = {
            "execution_timestamp": datetime.now().isoformat(),
            "fresh_start": False,
            "buying_power": 0,
            "allowed_symbols": [],
            "filtered_symbols": [],
            "current_positions": [],
            "state_dict": {},
            "put_options": [],
            "call_options": [],
            "sold_puts": [],
            "sold_calls": [],
            "trades": [],
            "summary": {
                "puts_sold": 0,
                "calls_sold": 0,
                "total_premium": 0.0
            }
        }
        
        logger.info(f"📊 Strategy logging enabled: {self.log_file}")
    
    def set_fresh_start(self, fresh_start: bool):
        """Set whether this is a fresh start execution."""
        if self.enabled:
            self.data["fresh_start"] = fresh_start
    
    def set_buying_power(self, buying_power: float):
        """Set the available buying power."""
        if self.enabled:
            self.data["buying_power"] = buying_power
    
    def set_allowed_symbols(self, symbols: List[str]):
        """Set the list of allowed trading symbols."""
        if self.enabled:
            self.data["allowed_symbols"] = symbols

    def set_filtered_symbols(self, symbols: List[str]):
        """Set the list of filtered symbols after buying power filter."""
        if self.enabled:
            self.data["filtered_symbols"] = symbols
            logger.info(f"📝 Logged {len(symbols)} filtered symbols: {symbols}")

    def add_current_positions(self, positions: List[Any]):
        """Add current position information."""
        if not self.enabled:
            return
            
        position_data = []
        for pos in positions:
            position_data.append({
                "symbol": pos.symbol,
                "side": str(pos.side),
                "qty": float(pos.qty),
                "avg_entry_price": float(pos.avg_entry_price) if pos.avg_entry_price else None,
                "current_price": float(pos.current_price) if pos.current_price else None,
                "unrealized_pl": float(pos.unrealized_pl) if pos.unrealized_pl else None,
                "market_value": float(pos.market_value) if pos.market_value else None
            })
        
        self.data["current_positions"] = position_data
    
    def add_state_dict(self, state_dict: Dict[str, Any]):
        """Add the strategy state dictionary."""
        if self.enabled:
            self.data["state_dict"] = state_dict

    def log_put_options(self, put_options: List[Dict[str, Any]]):
        """Log the available put options."""
        if self.enabled:
            self.data["put_options"] = put_options
            logger.info(f"📝 Logged {len(put_options)} put options")

    def log_call_options(self, call_options: List[Dict[str, Any]]):
        """Log the available call options."""
        if self.enabled:
            self.data["call_options"] = call_options
            logger.info(f"📝 Logged {len(call_options)} call options")

    def log_sold_puts(self, sold_puts: List[Dict[str, Any]]):
        """Log the sold put options."""
        if self.enabled:
            self.data["sold_puts"].extend(sold_puts)
            logger.info(f"📝 Logged {len(sold_puts)} sold puts")

    def log_sold_calls(self, sold_call: Dict[str, Any]):
        """Log a sold call option."""
        if self.enabled:
            self.data["sold_calls"].append(sold_call)
            logger.info(f"📝 Logged sold call: {sold_call.get('symbol', 'Unknown')}")
    
    def log_trade(self, trade_type: str, symbol: str, contract_symbol: str, 
                  strike: float, premium: float, expiry: str, quantity: int = 1):
        """
        Log a trade execution.
        
        Args:
            trade_type (str): 'PUT' or 'CALL'
            symbol (str): Underlying symbol
            contract_symbol (str): Full option contract symbol
            strike (float): Strike price
            premium (float): Premium collected
            expiry (str): Expiration date
            quantity (int): Number of contracts
        """
        if not self.enabled:
            return
            
        trade_data = {
            "timestamp": datetime.now().isoformat(),
            "type": trade_type.upper(),
            "symbol": symbol,
            "contract_symbol": contract_symbol,
            "strike": strike,
            "premium": premium,
            "expiry": expiry,
            "quantity": quantity
        }
        
        self.data["trades"].append(trade_data)
        
        # Update summary
        if trade_type.upper() == "PUT":
            self.data["summary"]["puts_sold"] += quantity
        elif trade_type.upper() == "CALL":
            self.data["summary"]["calls_sold"] += quantity
        
        self.data["summary"]["total_premium"] += premium
        
        logger.info(f"📝 Logged {trade_type} trade: {symbol} ${strike} for ${premium:.2f}")
    
    def save(self):
        """Save the log data to file."""
        if not self.enabled or not self.log_file:
            return
            
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            logger.info(f"💾 Strategy log saved: {self.log_file}")
            
        except Exception as e:
            logger.error(f"Failed to save strategy log: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get the current execution summary."""
        if self.enabled:
            return self.data["summary"].copy()
        return {"puts_sold": 0, "calls_sold": 0, "total_premium": 0.0}
