# 🤖 Fully Automated 24/7 Options Wheel Bot Guide

This guide explains how to set up and run the Options Wheel Bot completely hands-free with Discord monitoring. Once configured, the bot will run 24/7, automatically execute trades when markets are open, and keep you informed via Discord.

## 🎯 How the Bot Works (Fully Automated)

### The Complete Automation Cycle

1. **🔄 Continuous Monitoring** (Every 15 minutes)
   - Bot checks if markets are open
   - Validates it's a trading day (not weekend/holiday)
   - Checks if options trading is allowed

2. **📊 Market Hours Validation**
   - **Market Open**: 9:30 AM - 4:00 PM ET, Monday-Friday
   - **Weekends**: Bot waits patiently, no execution
   - **Holidays**: Automatically recognized and skipped
   - **After Hours**: No options trading allowed, bot waits

3. **💼 Strategy Execution** (When markets are open)
   - **Check Positions**: Reviews current stock holdings
   - **Sell Covered Calls**: If you own 100+ shares of any stock
   - **Sell Cash-Secured Puts**: On your target stocks with available buying power
   - **Risk Management**: Respects your buying power limits
   - **Position Tracking**: Logs all trades and positions

4. **📱 Discord Notifications** (Real-time)
   - **Bot Status**: Startup, execution, shutdown
   - **Trade Alerts**: Every put/call sold with details
   - **Market Updates**: When markets are closed
   - **Errors**: Any issues that need attention
   - **Daily Summaries**: End-of-day execution reports

5. **🛡️ Safety Features**
   - **Daily Limits**: Maximum 4 executions per day (configurable)
   - **Market Hours Only**: No trades outside trading hours
   - **Error Recovery**: Continues running after minor issues
   - **Graceful Shutdown**: Handles system restarts safely

## 🚀 Quick Setup (5 Minutes)

### Step 1: Configure Your Environment

Create a `.env` file in your project directory:

```env
# Alpaca Trading Credentials
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
IS_PAPER=true  # IMPORTANT: Start with paper trading!

# Discord Notifications (for 24/7 monitoring)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
DISCORD_NOTIFICATIONS_ENABLED=true
```

### Step 2: Set Your Trading Symbols

Edit `config/symbol_list.txt` with stocks you want to trade:

```
SIRI
NOK
VALE
NIO
SOFI
F
T
```

*These are low-cost stocks suitable for paper trading with small accounts.*

### Step 3: Test Your Setup

```powershell
# Test Discord notifications
python -m scripts.run_strategy --test-discord

# Test market hours detection
python -m scripts.run_strategy --test-market-hours

# Run complete system test
python -m scripts.system_test
```

### Step 4: Start 24/7 Mode

```powershell
# Start fully automated 24/7 operation
python -m scripts.run_strategy --continuous --strat-log --log-to-file
```

**That's it! Your bot is now running 24/7! 🎉**

## 📱 Setting Up Discord (Required for 24/7 Monitoring)

### Create Discord Webhook (2 minutes)

1. **Create/Use Discord Server**
   - Create a new server or use existing one
   - Create a channel like `#trading-bot`

2. **Create Webhook**
   - Go to Channel Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Name it "Options Wheel Bot"
   - Copy the webhook URL

3. **Add to .env File**
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/your-webhook-url
   DISCORD_NOTIFICATIONS_ENABLED=true
   ```

### What You'll See in Discord

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

📉 Put Executed
Underlying: SIRI
Contract: SIRI250620P00003500
Strike: $3.5
Premium Collected: $0.15
Expiry: 13 days

✅ Execution Complete
Strategy execution completed (Run 1/4)
Puts Sold: 2 contracts
Total Premium Collected: $45.00
```

## ⚙️ Recommended Settings for Different Use Cases

### 🧪 Paper Trading (Learning Mode)
```powershell
# Conservative: Once per day, full logging
python -m scripts.run_strategy --continuous --max-runs-per-day 1 --check-interval 60 --strat-log --log-to-file --log-level INFO
```

### 💰 Small Account ($500-2000)
```powershell
# Active but careful: 2-3 times per day
python -m scripts.run_strategy --continuous --max-runs-per-day 2 --check-interval 30 --strat-log --log-to-file
```

### 📈 Active Trading ($2000+)
```powershell
# Full activity: Default settings
python -m scripts.run_strategy --continuous --strat-log --log-to-file
```

### 🔍 Debug Mode (Troubleshooting)
```powershell
# Maximum logging for issues
python -m scripts.run_strategy --continuous --log-level DEBUG --log-to-file --max-runs-per-day 1
```

## 📊 Command Options Explained

| Option | Description | Default | Recommendation |
|--------|-------------|---------|---------------|
| `--continuous` | Enable 24/7 mode | ❌ | ✅ **Required** |
| `--check-interval N` | Check market every N minutes | 15 | 15-30 minutes |
| `--max-runs-per-day N` | Daily execution limit | 4 | 1-4 depending on account |
| `--strat-log` | Save trade logs | ❌ | ✅ **Recommended** |
| `--log-to-file` | Save debug logs | ❌ | ✅ **Recommended** |
| `--log-level LEVEL` | Logging detail | INFO | INFO or DEBUG |

## 🕐 Daily Operation Schedule

### Typical 24/7 Bot Day

**6:00 AM ET** - Bot checks market status
- 📱 Discord: "Market closed, opens in 3.5 hours"

**9:30 AM ET** - Market opens
- 📱 Discord: "🚀 Execution Starting (Run 1/4)"
- 🤖 Bot executes strategy
- 📱 Discord: "✅ Execution Complete - 3 puts sold, $127 premium"

**12:00 PM ET** - Midday check
- 🤖 Bot checks positions, may execute again if conditions met

**4:00 PM ET** - Market closes
- 📱 Discord: "⏰ Market closed, next open tomorrow 9:30 AM"

**Evening/Night** - Bot continues monitoring
- 🤖 Checks every 15 minutes but no execution (markets closed)

**Weekends** - Bot waits patiently
- 📱 Discord: "Market closed, next open Monday 9:30 AM"

## 🎯 What the Bot Actually Does

### When Markets Are Open:

1. **📊 Position Analysis**
   ```
   Checking current positions...
   Found: 100 shares SIRI at $3.45
   Found: 200 shares NOK at $4.12
   ```

2. **📈 Sell Covered Calls** (if you own stocks)
   ```
   Selling covered call on SIRI...
   Strike: $4.00, Expiry: 14 days
   Premium: $0.08 per share ($8 total)
   ```

3. **📉 Sell Cash-Secured Puts** (with available cash)
   ```
   Available buying power: $1,247
   Targeting: VALE, NIO, SOFI
   Selling put on VALE...
   Strike: $11.00, Expiry: 21 days
   Premium: $0.22 per share ($22 total)
   ```

4. **💾 Record Everything**
   - Logs saved to files
   - Discord notifications sent
   - Strategy state updated

### When Markets Are Closed:

1. **⏰ Status Check**
   ```
   Market status: closed
   Phase: afterhours
   Next open: Monday 9:30 AM ET
   ```

2. **💤 Wait Mode**
   - No trading attempts
   - Continue monitoring
   - Send periodic Discord updates

## 🛡️ Safety & Risk Management

### Built-in Protections

- **🚫 No Weekend Trading**: Impossible to trade when markets closed
- **🏦 Buying Power Limits**: Never exceeds your available cash
- **📊 Position Limits**: One contract per symbol (simplified risk)
- **⏰ Market Hours Only**: Options only trade during regular hours
- **🔄 Daily Limits**: Prevents over-trading (default: 4 executions/day)

### What Could Go Wrong & How Bot Handles It

- **❌ API Error**: Bot logs error, sends Discord alert, continues running
- **📉 Market Crash**: Bot continues normal operation (puts might get assigned)
- **🔌 Internet Issue**: Bot will reconnect when service restored
- **💻 Computer Restart**: Just restart the bot, it picks up where it left off
- **📱 Discord Down**: Bot continues trading, just no notifications

## 🚀 Starting Your 24/7 Bot

### Final Command (Copy & Paste)

```powershell
# Navigate to your bot directory
cd "C:\Users\Cyril Lutziger\OneDrive\Dokumente\GitHub\options-wheel"

# Start 24/7 automated operation
python -m scripts.run_strategy --continuous --strat-log --log-to-file --log-level INFO
```

### You'll See This Output:

```
Starting Options Wheel Bot in continuous 24/7 mode...
✅ Discord notifications are enabled
📊 Check interval: 15 minutes
🎯 Max runs per day: 4
⏰ Market Status at 2025-06-07 10:59:20 EDT
  Trading Day: False
  Market Phase: closed
  Can Trade Options: False
  Next Market Open: 2025-06-09 09:30:00 EDT
🔄 Starting demo scheduler...
💤 Sleeping for 15 minutes...
```

### How to Stop the Bot

- **Ctrl+C** in the terminal (graceful shutdown)
- **Close terminal window** (also works)
- Bot will send Discord notification when stopping

## 📈 Monitoring Your Bot

### Discord Notifications You'll Receive

1. **🤖 Bot Started** - When you start the bot
2. **🚀 Execution Starting** - Before each trade cycle
3. **📉📈 Trade Alerts** - For every put/call sold
4. **✅ Execution Complete** - After each trade cycle
5. **⏰ Market Closed** - When trades are skipped
6. **❌ Error Alerts** - If something goes wrong
7. **🛑 Bot Stopped** - When you stop the bot

### Log Files (Optional but Recommended)

With `--log-to-file`, you'll get detailed logs saved to disk:
- **Strategy logs**: JSON files with trade history
- **Runtime logs**: Detailed execution logs
- **Error logs**: Any issues for troubleshooting

## 🎉 Congratulations!

Your Options Wheel Bot is now running 24/7! Here's what happens next:

1. **📱 Check Discord** - You'll get notifications for all bot activity
2. **🕘 Wait for Market Open** - Bot will execute when markets open
3. **📊 Monitor Positions** - Check your broker account for trades
4. **📈 Collect Premiums** - Bot will sell puts/calls and collect income
5. **🔄 Rinse & Repeat** - Bot continues automatically every trading day

### Important Reminders

- ✅ **Start with paper trading** (`IS_PAPER=true`)
- ✅ **Monitor Discord notifications** daily
- ✅ **Review logs** periodically
- ✅ **Start with small amounts** until comfortable
- ✅ **Understand the wheel strategy** before going live

**Your bot is now earning income 24/7 while you sleep! 🌙💰**
