# 24/7 Automation Guide

This guide explains how to use the Options Wheel Bot's 24/7 continuous automation mode with market hours awareness.

## 🌟 New Features

### 1. Market Hours Validation
- **Automatic Detection**: The bot automatically detects when markets are open/closed
- **Options Trading Hours**: Only executes trades during regular market hours (9:30 AM - 4:00 PM ET)
- **Holiday Awareness**: Recognizes US market holidays and skips trading
- **Timezone Handling**: Properly handles Eastern Time conversions regardless of your local timezone

### 2. Continuous Scheduler
- **24/7 Operation**: Runs continuously, checking market status every 15 minutes (configurable)
- **Smart Execution**: Only executes trades when markets are open
- **Daily Limits**: Configurable maximum executions per trading day (default: 4)
- **Graceful Shutdown**: Handles interrupts and shutdowns safely

### 3. Enhanced Discord Notifications
- **Scheduler Status**: Get notified when the bot starts, executes, or shuts down
- **Market Status**: Receive alerts when markets are closed
- **Execution Tracking**: Track daily execution counts and limits

## 🚀 Quick Start - 24/7 Mode

### Basic Usage
```powershell
# Start the bot in continuous 24/7 mode
python -m scripts.run_strategy --continuous

# With custom check interval (30 minutes)
python -m scripts.run_strategy --continuous --check-interval 30

# With custom daily execution limit (2 times per day)
python -m scripts.run_strategy --continuous --max-runs-per-day 2
```

### Recommended Settings for Paper Trading
```powershell
# Conservative approach: Check every 30 minutes, max 2 executions per day
python -m scripts.run_strategy --continuous --check-interval 30 --max-runs-per-day 2 --strat-log --log-to-file

# Aggressive approach: Check every 15 minutes, max 4 executions per day
python -m scripts.run_strategy --continuous --check-interval 15 --max-runs-per-day 4 --strat-log --log-to-file
```

## 🛠️ Command Line Options

### New Automation Options
- `--continuous`: Enable 24/7 continuous mode
- `--check-interval N`: Check market status every N minutes (default: 15)
- `--max-runs-per-day N`: Maximum strategy executions per trading day (default: 4)
- `--test-market-hours`: Test market hours checker and exit

### Existing Options (still available)
- `--fresh-start`: Liquidate all positions before running
- `--strat-log`: Enable strategy JSON logging
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-to-file`: Write logs to file
- `--test-discord`: Test Discord webhook functionality

## 📊 Market Hours Information

### Regular Trading Hours
- **Market Open**: 9:30 AM ET
- **Market Close**: 4:00 PM ET
- **Trading Days**: Monday - Friday (excluding holidays)

### Options Trading
- **Options trades are only allowed during regular market hours**
- **Pre-market (4:00 AM - 9:30 AM ET)**: Options trading not available
- **After-hours (4:00 PM - 8:00 PM ET)**: Options trading not available

### Recognized Holidays (2024-2025)
- New Year's Day
- Martin Luther King Jr. Day
- Presidents Day
- Good Friday
- Memorial Day
- Juneteenth
- Independence Day
- Labor Day
- Thanksgiving
- Christmas

## 🔄 How Continuous Mode Works

### Execution Logic
1. **Market Check**: Every 15 minutes (or your custom interval), check if markets are open
2. **Trading Validation**: Only execute when options trading is allowed
3. **Daily Limits**: Track executions per day to avoid over-trading
4. **Smart Scheduling**: Execute once when market opens (if configured)
5. **Status Updates**: Log status every hour and send Discord notifications

### Execution Triggers
- **Market Open**: Execute once when market opens (default behavior)
- **Daily Reset**: Reset execution counter each trading day
- **Error Recovery**: Continue running even if individual executions fail

## 📱 Discord Integration

### Notification Types in Continuous Mode
- **🤖 Scheduler Started**: When continuous mode begins
- **🚀 Execution Starting**: Before each strategy execution
- **✅ Execution Complete**: After successful execution
- **⏰ Market Closed**: When execution is skipped due to market hours
- **❌ Errors**: Any errors during execution
- **🛑 Scheduler Shutdown**: When the bot stops

### Sample Discord Messages
```
🤖 Scheduler Started
Options Wheel Bot started in continuous mode
📊 Check interval: 15 minutes
🎯 Max runs per day: 4

⏰ Market Closed
Options trading not allowed at this time
Market Phase: closed
Next Market Open: 2025-06-09 09:30:00 EDT

🚀 Execution Starting
Starting strategy execution (Run 1/4)

✅ Execution Complete
Strategy execution completed (Run 1/4)
```

## ⚙️ Configuration Examples

### Conservative Day Trading Setup
```powershell
# Check every hour, execute max 1 time per day at market open
python -m scripts.run_strategy --continuous --check-interval 60 --max-runs-per-day 1
```

### Active Trading Setup
```powershell
# Check every 15 minutes, execute up to 4 times per day
python -m scripts.run_strategy --continuous --check-interval 15 --max-runs-per-day 4
```

### Paper Trading with Full Logging
```powershell
# Full logging and Discord notifications for testing
python -m scripts.run_strategy --continuous --strat-log --log-to-file --log-level DEBUG
```

## 🛡️ Safety Features

### Market Hours Protection
- **No Weekend Trading**: Automatically skips weekends
- **Holiday Awareness**: Respects market holidays
- **Options Hours Only**: Only trades during regular market hours
- **Timezone Safety**: Handles daylight saving time changes

### Execution Limits
- **Daily Caps**: Prevents over-trading with configurable daily limits
- **Error Recovery**: Continues running after individual failures
- **Graceful Shutdown**: Properly handles Ctrl+C and system signals

### Monitoring
- **Regular Status Updates**: Hourly status logs
- **Discord Alerts**: Real-time notifications for all events
- **Detailed Logging**: Optional file logging with configurable levels

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Executing
- **Check Market Hours**: Use `--test-market-hours` to verify market status
- **Verify Daily Limits**: Check if you've hit the daily execution limit
- **Review Logs**: Enable `--log-level DEBUG` for detailed information

#### Discord Not Working
- **Test Discord**: Use `--test-discord` to verify webhook configuration
- **Check .env File**: Ensure `DISCORD_WEBHOOK_URL` is set correctly
- **Verify Enabled**: Confirm `DISCORD_NOTIFICATIONS_ENABLED=true`

#### Market Hours Issues
- **Timezone Problems**: Market hours checker uses Eastern Time automatically
- **Holiday Questions**: Check the holiday list in the documentation above

### Testing Commands

```powershell
# Test market hours functionality
python -m scripts.run_strategy --test-market-hours

# Test Discord integration
python -m scripts.run_strategy --test-discord

# Test normal execution (one-time)
python -m scripts.run_strategy --strat-log

# Test continuous mode with debug logging
python -m scripts.run_strategy --continuous --log-level DEBUG --max-runs-per-day 1
```

## 📈 Best Practices

### For Paper Trading
- Start with `--max-runs-per-day 1` to limit exposure
- Use `--check-interval 30` or higher to reduce API calls
- Enable full logging: `--strat-log --log-to-file --log-level INFO`

### For Live Trading (when ready)
- Test thoroughly with paper trading first
- Use conservative daily limits initially
- Monitor Discord notifications closely
- Have a plan for weekends and holidays

### Performance Optimization
- Use longer check intervals (30-60 minutes) to reduce resource usage
- Enable file logging to track performance over time
- Monitor your VPS/server resources if running remotely

## 🚨 Important Notes

⚠️ **Always test with paper trading first!**

⚠️ **Monitor the bot regularly, especially in the first few days**

⚠️ **Have your Discord notifications configured for real-time monitoring**

⚠️ **Remember that options trading is only available during regular market hours**

⚠️ **The bot will continue running 24/7 but only execute during market hours**

## 📞 Support

If you encounter issues:
1. Check the logs (enable `--log-to-file`)
2. Test individual components (`--test-market-hours`, `--test-discord`)
3. Review Discord notifications for error messages
4. Use debug logging (`--log-level DEBUG`) for detailed troubleshooting
