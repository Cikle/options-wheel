"""
Continuous scheduler for 24/7 options wheel bot automation.
"""
import time
import datetime
import logging
import signal
import sys
from typing import Callable, Optional
from pathlib import Path

from core.market_hours import MarketHoursChecker
from logging.discord_notifier import DiscordNotifier

logger = logging.getLogger(__name__)

class ContinuousScheduler:
    """
    Manages continuous execution of the options wheel strategy with market hours awareness.
    """
    
    def __init__(
        self, 
        strategy_function: Callable,
        check_interval_minutes: int = 15,
        run_at_market_open: bool = True,
        max_runs_per_day: int = 4,
        discord_notifier: Optional[DiscordNotifier] = None
    ):
        """
        Initialize the continuous scheduler.
        
        Args:
            strategy_function: The function to execute (should be the main strategy)
            check_interval_minutes: How often to check market status (minutes)
            run_at_market_open: Whether to execute immediately when market opens
            max_runs_per_day: Maximum number of strategy executions per trading day
            discord_notifier: Optional Discord notifier for status updates
        """
        self.strategy_function = strategy_function
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.run_at_market_open = run_at_market_open
        self.max_runs_per_day = max_runs_per_day
        self.market_checker = MarketHoursChecker()
        self.discord_notifier = discord_notifier
        
        # State tracking
        self.is_running = False
        self.last_run_date = None
        self.runs_today = 0
        self.last_market_status = None
        self.shutdown_notified = False  # Track if shutdown notification was sent
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        # Don't send notification here - let stop() handle it to prevent duplicates
        self.stop()
        sys.exit(0)
    
    def _reset_daily_counter(self):
        """Reset the daily run counter if it's a new trading day."""
        current_date = datetime.datetime.now(self.market_checker.eastern_tz).date()
        
        if self.last_run_date != current_date:
            self.runs_today = 0
            self.last_run_date = current_date
            logger.info(f"New trading day detected: {current_date}. Reset run counter.")
    
    def _should_execute_strategy(self) -> tuple[bool, str]:
        """
        Determine if the strategy should be executed now.
        
        Returns:
            tuple: (should_execute: bool, reason: str)
        """
        # Check if we've hit the daily limit
        if self.runs_today >= self.max_runs_per_day:
            return False, f"Daily limit reached ({self.runs_today}/{self.max_runs_per_day})"
        
        # Check if options trading is allowed (market hours)
        if not self.market_checker.can_trade_options():
            return False, "Options trading not allowed (market closed)"
        
        # If we want to run at market open, check if market just opened
        if self.run_at_market_open:
            current_status = self.market_checker.get_market_status()
            
            # If market just opened (status changed from closed to open)
            if (self.last_market_status and 
                not self.last_market_status.get('is_market_open', False) and 
                current_status['is_market_open']):
                return True, "Market just opened"
          # For now, we'll execute once when market opens
        # This can be expanded with more sophisticated scheduling logic
        if self.runs_today == 0 and self.market_checker.is_market_open():
            return True, "First run of the trading day"
        
        return False, "No execution trigger met"
    
    def _execute_strategy(self):
        """Execute the strategy function with error handling."""
        try:
            logger.info("Executing options wheel strategy...")
            
            if self.discord_notifier:
                self.discord_notifier.send_scheduler_notification(
                    "execution_start",
                    f"🚀 Starting strategy execution (Run {self.runs_today + 1}/{self.max_runs_per_day})"
                )
            
            # Execute the strategy
            self.strategy_function()
            
            # Update counters
            self.runs_today += 1
            
            logger.info(f"Strategy execution completed successfully. Runs today: {self.runs_today}")
            
            if self.discord_notifier:
                self.discord_notifier.send_scheduler_notification(
                    "execution_complete",
                    f"✅ Strategy execution completed (Run {self.runs_today}/{self.max_runs_per_day})"
                )
                
        except Exception as e:
            logger.error(f"Error during strategy execution: {e}")
            
            # Don't send duplicate error notification here since the main strategy
            # execution already sends its own error notification via execute_strategy_once()
            # Just log the error and continue with scheduler operation
    
    def _log_status_update(self):
        """Log periodic status updates."""
        status = self.market_checker.get_market_status()
        
        logger.info("="*60)
        logger.info("CONTINUOUS SCHEDULER STATUS UPDATE")
        logger.info("="*60)
        logger.info(f"Current Time (ET): {status['current_time_et']}")
        logger.info(f"Market Phase: {status['market_phase'].upper()}")
        logger.info(f"Can Trade Options: {status['can_trade_options']}")
        logger.info(f"Runs Today: {self.runs_today}/{self.max_runs_per_day}")
        
        if not status['can_trade_options']:
            logger.info(f"Next Market Open: {status['next_market_open']}")
            logger.info(f"Time Until Open: {status['time_until_market_open']}")
        
        logger.info("="*60)
    
    def start(self):
        """Start the continuous scheduler."""
        logger.info("Starting continuous options wheel scheduler...")
        logger.info(f"Check interval: {self.check_interval // 60} minutes")
        logger.info(f"Max runs per day: {self.max_runs_per_day}")
        
        if self.discord_notifier:
            self.discord_notifier.send_scheduler_notification(
                "startup",
                f"🤖 Options Wheel Bot started in continuous mode\n" +
                f"📊 Check interval: {self.check_interval // 60} minutes\n" +
                f"🎯 Max runs per day: {self.max_runs_per_day}"
            )
        
        self.is_running = True
        self._reset_daily_counter()
        
        # Log initial market status
        self._log_status_update()
        
        while self.is_running:
            try:
                # Reset daily counter if needed
                self._reset_daily_counter()
                
                # Check if we should execute the strategy
                should_execute, reason = self._should_execute_strategy()
                
                logger.debug(f"Execution check: {should_execute} - {reason}")
                
                if should_execute:
                    self._execute_strategy()
                else:
                    logger.debug(f"Skipping execution: {reason}")
                
                # Update market status for next iteration
                self.last_market_status = self.market_checker.get_market_status()
                
                # Log status update every hour (4 cycles of 15 minutes)
                current_time = datetime.datetime.now()
                if current_time.minute in [0, 15, 30, 45] and current_time.second < 30:
                    self._log_status_update()
                
                # Wait for the next check
                logger.debug(f"Sleeping for {self.check_interval // 60} minutes...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt. Stopping scheduler...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in scheduler loop: {e}")
                if self.discord_notifier:
                    self.discord_notifier.send_error_notification(
                        str(e), 
                        "Continuous Scheduler - Main Loop"
                    )
                # Continue running after error
                time.sleep(60)  # Wait 1 minute before retrying
        
        self.stop()
    def stop(self):
        """Stop the continuous scheduler."""
        logger.info("Stopping continuous scheduler...")
        self.is_running = False
        
        # Only send shutdown notification once
        if self.discord_notifier and not self.shutdown_notified:
            self.shutdown_notified = True
            self.discord_notifier.send_scheduler_notification(
                "shutdown",
                f"🛑 Options Wheel Bot stopped\n" +
                f"📊 Runs completed today: {self.runs_today}"
            )

def create_scheduler_with_strategy(
    strategy_args,
    check_interval_minutes: int = 15,
    max_runs_per_day: int = 4
) -> ContinuousScheduler:
    """
    Create a scheduler with the options wheel strategy.
    
    Args:
        strategy_args: Arguments to pass to the strategy
        check_interval_minutes: How often to check market status
        max_runs_per_day: Maximum executions per trading day
        
    Returns:
        ContinuousScheduler: Configured scheduler instance
    """
    # Create a wrapper function that will be called by the scheduler
    def strategy_wrapper():
        from scripts.run_strategy import execute_strategy_once
        execute_strategy_once(strategy_args)
    
    # Initialize Discord notifier
    discord_notifier = DiscordNotifier()
    
    return ContinuousScheduler(
        strategy_function=strategy_wrapper,
        check_interval_minutes=check_interval_minutes,
        max_runs_per_day=max_runs_per_day,
        discord_notifier=discord_notifier
    )
