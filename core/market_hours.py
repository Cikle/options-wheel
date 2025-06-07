"""
Market hours validation and trading schedule utilities.
"""
import datetime
import pytz
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# US Market holidays (simplified list - can be expanded)
US_MARKET_HOLIDAYS_2024 = [
    datetime.date(2024, 1, 1),   # New Year's Day
    datetime.date(2024, 1, 15),  # Martin Luther King Jr. Day
    datetime.date(2024, 2, 19),  # Presidents Day
    datetime.date(2024, 3, 29),  # Good Friday
    datetime.date(2024, 5, 27),  # Memorial Day
    datetime.date(2024, 6, 19),  # Juneteenth
    datetime.date(2024, 7, 4),   # Independence Day
    datetime.date(2024, 9, 2),   # Labor Day
    datetime.date(2024, 11, 28), # Thanksgiving
    datetime.date(2024, 12, 25), # Christmas
]

US_MARKET_HOLIDAYS_2025 = [
    datetime.date(2025, 1, 1),   # New Year's Day
    datetime.date(2025, 1, 20),  # Martin Luther King Jr. Day
    datetime.date(2025, 2, 17),  # Presidents Day
    datetime.date(2025, 4, 18),  # Good Friday
    datetime.date(2025, 5, 26),  # Memorial Day
    datetime.date(2025, 6, 19),  # Juneteenth
    datetime.date(2025, 7, 4),   # Independence Day
    datetime.date(2025, 9, 1),   # Labor Day
    datetime.date(2025, 11, 27), # Thanksgiving
    datetime.date(2025, 12, 25), # Christmas
]

ALL_HOLIDAYS = US_MARKET_HOLIDAYS_2024 + US_MARKET_HOLIDAYS_2025

class MarketHoursChecker:
    """Check if markets are open and provide market schedule information."""
    
    def __init__(self):
        self.eastern_tz = pytz.timezone('US/Eastern')
        self.utc_tz = pytz.UTC
        
    def is_market_open(self, dt: Optional[datetime.datetime] = None) -> bool:
        """
        Check if the market is currently open.
        
        Args:
            dt: Optional datetime to check. If None, uses current time.
            
        Returns:
            bool: True if market is open, False otherwise
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        # Convert to Eastern Time
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        # Check if it's a weekend
        if eastern_dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        # Check if it's a holiday
        if eastern_dt.date() in ALL_HOLIDAYS:
            return False
            
        # Regular market hours: 9:30 AM - 4:00 PM ET
        market_open = eastern_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = eastern_dt.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= eastern_dt < market_close
    
    def is_premarket_open(self, dt: Optional[datetime.datetime] = None) -> bool:
        """
        Check if pre-market is open (4:00 AM - 9:30 AM ET).
        
        Args:
            dt: Optional datetime to check. If None, uses current time.
            
        Returns:
            bool: True if pre-market is open, False otherwise
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        # Check if it's a weekend
        if eastern_dt.weekday() >= 5:
            return False
            
        # Check if it's a holiday
        if eastern_dt.date() in ALL_HOLIDAYS:
            return False
            
        # Pre-market hours: 4:00 AM - 9:30 AM ET
        premarket_open = eastern_dt.replace(hour=4, minute=0, second=0, microsecond=0)
        market_open = eastern_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        
        return premarket_open <= eastern_dt < market_open
    
    def is_afterhours_open(self, dt: Optional[datetime.datetime] = None) -> bool:
        """
        Check if after-hours trading is open (4:00 PM - 8:00 PM ET).
        
        Args:
            dt: Optional datetime to check. If None, uses current time.
            
        Returns:
            bool: True if after-hours is open, False otherwise
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        # Check if it's a weekend
        if eastern_dt.weekday() >= 5:
            return False
            
        # Check if it's a holiday
        if eastern_dt.date() in ALL_HOLIDAYS:
            return False
            
        # After-hours: 4:00 PM - 8:00 PM ET
        market_close = eastern_dt.replace(hour=16, minute=0, second=0, microsecond=0)
        afterhours_close = eastern_dt.replace(hour=20, minute=0, second=0, microsecond=0)
        
        return market_close <= eastern_dt < afterhours_close
    
    def can_trade_options(self, dt: Optional[datetime.datetime] = None) -> bool:
        """
        Check if options trading is allowed.
        Options are generally only tradeable during regular market hours.
        
        Args:
            dt: Optional datetime to check. If None, uses current time.
            
        Returns:
            bool: True if options trading is allowed, False otherwise
        """
        return self.is_market_open(dt)
    
    def get_next_market_open(self, dt: Optional[datetime.datetime] = None) -> datetime.datetime:
        """
        Get the next market open time.
        
        Args:
            dt: Optional datetime to start from. If None, uses current time.
            
        Returns:
            datetime: Next market open time in Eastern timezone
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        # Start with today's market open
        next_open = eastern_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # If market hasn't opened today, return today's open time
        if eastern_dt < next_open and eastern_dt.weekday() < 5 and eastern_dt.date() not in ALL_HOLIDAYS:
            return next_open
        
        # Otherwise, find the next business day
        days_ahead = 1
        while True:
            candidate_date = eastern_dt.date() + datetime.timedelta(days=days_ahead)
            candidate_dt = eastern_dt.replace(
                year=candidate_date.year,
                month=candidate_date.month,
                day=candidate_date.day,
                hour=9,
                minute=30,
                second=0,
                microsecond=0
            )
            
            # Check if it's not a weekend or holiday
            if candidate_dt.weekday() < 5 and candidate_date not in ALL_HOLIDAYS:
                return candidate_dt
            
            days_ahead += 1
            if days_ahead > 10:  # Safety check
                break
        
        return next_open  # Fallback
    
    def get_time_until_market_open(self, dt: Optional[datetime.datetime] = None) -> datetime.timedelta:
        """
        Get the time remaining until the next market open.
        
        Args:
            dt: Optional datetime to start from. If None, uses current time.
            
        Returns:
            timedelta: Time until next market open
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        next_open = self.get_next_market_open(dt)
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        return next_open - eastern_dt
    
    def get_market_status(self, dt: Optional[datetime.datetime] = None) -> Dict[str, any]:
        """
        Get comprehensive market status information.
        
        Args:
            dt: Optional datetime to check. If None, uses current time.
            
        Returns:
            dict: Market status information
        """
        if dt is None:
            dt = datetime.datetime.now(self.utc_tz)
        
        eastern_dt = dt.astimezone(self.eastern_tz)
        
        status = {
            'current_time_et': eastern_dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'is_trading_day': eastern_dt.weekday() < 5 and eastern_dt.date() not in ALL_HOLIDAYS,
            'is_market_open': self.is_market_open(dt),
            'is_premarket_open': self.is_premarket_open(dt),
            'is_afterhours_open': self.is_afterhours_open(dt),
            'can_trade_options': self.can_trade_options(dt),
            'next_market_open': self.get_next_market_open(dt).strftime('%Y-%m-%d %H:%M:%S %Z'),
            'time_until_market_open': str(self.get_time_until_market_open(dt))
        }
        
        if status['is_market_open']:
            status['market_phase'] = 'regular_hours'
        elif status['is_premarket_open']:
            status['market_phase'] = 'premarket'
        elif status['is_afterhours_open']:
            status['market_phase'] = 'afterhours'
        else:
            status['market_phase'] = 'closed'
        
        return status

def log_market_status():
    """Log current market status information."""
    checker = MarketHoursChecker()
    status = checker.get_market_status()
    
    logger.info(f"Market Status at {status['current_time_et']}")
    logger.info(f"  Trading Day: {status['is_trading_day']}")
    logger.info(f"  Market Phase: {status['market_phase']}")
    logger.info(f"  Can Trade Options: {status['can_trade_options']}")
    logger.info(f"  Next Market Open: {status['next_market_open']}")
    
    if not status['can_trade_options']:
        logger.info(f"  Time Until Market Open: {status['time_until_market_open']}")

if __name__ == "__main__":
    # Test the market hours checker
    log_market_status()
