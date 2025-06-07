# Automated Wheel Strategy

Welcome to the Wheel Strategy automation project!
This script is designed to help you trade the classic ["wheel" options strategy](https://alpaca.markets/learn/options-wheel-strategy) with as little manual work as possible using the [Alpaca Trading API](https://docs.alpaca.markets/).

---

## Strategy Logic

Here's the basic idea:

1. **Sell cash-secured puts** on stocks you wouldn't mind owning.
2. If you **get assigned**, buy the stock.
3. Then **sell covered calls** on the stock you own.
4. Keep collecting premiums until the stock gets called away.
5. Repeat the cycle!

This code helps pick the right puts and calls to sell, tracks your positions, and automatically turns the wheel to the next step.

---

## How to Run the Code

1. **Clone the repository:**

   ```bash
   git clone https://github.com/alpacahq/options-wheel.git
   cd options-wheel
   ```

2. **Create a virtual environment using [`uv`](https://github.com/astral-sh/uv):**

   ```bash
   uv venv
   source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
   ```

3. **Install the required packages:**

   ```bash
   uv pip install -e .
   ```

4. **Set up your API credentials:**

   Create a `.env` file in the project root with the following content:

   ```env
   ALPACA_API_KEY=your_public_key
   ALPACA_SECRET_KEY=your_private_key
   IS_PAPER=true  # Set to false if using a live account
   
   # Discord Webhook (Optional)
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
   DISCORD_NOTIFICATIONS_ENABLED=true  # Set to false to disable Discord notifications
   ```

   Your credentials will be loaded from `.env` automatically.   **Discord Webhook Setup (Optional):**
   
   To receive Discord notifications when the bot executes trades:
   
   1. Create a Discord server or use an existing one
   2. Go to Server Settings → Integrations → Webhooks
   3. Click "New Webhook" and configure it
   4. Copy the webhook URL and add it to your `.env` file
   5. Set `DISCORD_NOTIFICATIONS_ENABLED=true`
   
   For detailed setup instructions, see [DISCORD_SETUP.md](./DISCORD_SETUP.md).
   
   The bot will send notifications for:
   - Strategy startup and completion
   - Trade executions (puts and calls sold)
   - Current positions updates
   - Error notifications

5. **Choose your symbols:**

   The strategy trades only the symbols listed in `config/symbol_list.txt`. Edit this file to include the tickers you want to run the Wheel strategy on — one symbol per line. Choose stocks you'd be comfortable holding long-term.

6. **Configure trading parameters:**

   Adjust values in `config/params.py` to customize things like buying power limits, options characteristics (e.g., greeks / expiry), and scoring thresholds. Each parameter is documented in the file.


7. **Run the strategy**

   Run the strategy (which assumes an empty or fully managed portfolio):
   
   ```bash
   run-strategy
   ```
   
   > **Tip:** On your first run, use `--fresh-start` to liquidate all existing positions and start clean.
   
   There are two types of logging:
   
   * **Strategy JSON logging** (`--strat-log`):
     Always saves detailed JSON files to disk for analyzing strategy performance.
   
   * **Runtime logging** (`--log-level` and `--log-to-file`):
     Controls console/file logs for monitoring the current run. Optional and configurable.
     **Flags:**
   
   * `--fresh-start` — Liquidate all positions before running (recommended first run).
   * `--strat-log` — Enable strategy JSON logging (always saved to disk).
   * `--log-level LEVEL` — Set runtime logging verbosity (default: INFO).
   * `--log-to-file` — Save runtime logs to file instead of console.
   * `--test-discord` — Test Discord webhook functionality and exit (useful for setup verification).
   
   Example:
   
   ```bash
   run-strategy --fresh-start --strat-log --log-level DEBUG --log-to-file
   ```
   
   **Testing Discord Integration:**
   
   To test if your Discord webhook is working correctly:
   
   ```bash
   run-strategy --test-discord
   ```
   
   This will send test messages to your Discord channel without executing any trades.
     For more info:
   
   ```bash
   run-strategy --help
   ```

---

## Discord Notifications

The bot can send real-time notifications to Discord when it executes trades or encounters issues. This is especially useful for monitoring your automated trading strategy.

### Notification Types

The Discord integration sends notifications for:

- **🚀 Bot Startup**: When the strategy begins execution
- **📈📉 Trade Executions**: When puts or calls are sold with details about the contract
- **📊 Position Updates**: Current portfolio positions and P&L
- **✅ Completion**: When strategy execution finishes with summary
- **❌ Errors**: When errors occur during execution

### Setup Instructions

1. **Create a Discord Webhook:**
   - Go to your Discord server
   - Navigate to Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Configure the webhook (name, channel, avatar)
   - Copy the webhook URL

2. **Configure Your .env File:**
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url_here
   DISCORD_NOTIFICATIONS_ENABLED=true
   ```

3. **Test the Integration:**
   ```bash
   run-strategy --test-discord
   ```

### Disabling Notifications

To disable Discord notifications, set `DISCORD_NOTIFICATIONS_ENABLED=false` in your `.env` file or simply omit the Discord configuration variables.

---

### What the Script Does

* Checks your current positions to identify any assignments and sells covered calls on those.
* Filters your chosen stocks based on buying power (you must be able to afford 100 shares per put).
* Scores put options using `core.strategy.score_options()`, which ranks by annualized return discounted by the probability of assignment.
* Places trades for the top-ranked options.

---

### Notes

* **Account state matters**: This strategy assumes full control of the account — all positions are expected to be managed by this script. For best results, start with a clean account (e.g. by using the `--fresh-start` flag).
* **One contract per symbol**: To simplify risk management, this implementation trades only one contract at a time per symbol. You can modify this logic in `core/strategy.py` to suit more advanced use cases.
* The **user agent** for API calls defaults to `OPTIONS-WHEEL` to help Alpaca track usage of runnable algos and improve user experience.  You can opt out by adjusting the `USER_AGENT` variable in `core/user_agent_mixin.py` — though we kindly hope you’ll keep it enabled to support ongoing improvements.  
* **Want to customize the strategy?** The `core/strategy.py` module is a great place to start exploring and modifying the logic.

---

## Automating the Wheel

Running the script once will only turn the wheel a single time. To keep it running as a long-term income strategy, you'll want to automate it to run several times per day. This can be done with a cron job on Mac or Linux.

### Setting Up a Cron Job (Mac / Linux) - Alternative Method

1. **Find the full path to the `run-strategy` command** by running:

   ```bash
   which run-strategy
   ```

   This will output something like:

   ```bash
   /Users/yourname/.local/share/virtualenvs/options-wheel-abc123/bin/run-strategy
   ```

2. **Open your crontab** for editing:

   ```bash
   crontab -e
   ```

3. **Add the following lines to run the strategy at 10:00 AM, 1:00 PM, and 3:30 PM on weekdays:**

   ```cron
   0 10 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_10am.log 2>&1
   0 13 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_1pm.log 2>&1
   30 15 * * 1-5 /full/path/to/run-strategy >> /path/to/logs/run_strategy_330pm.log 2>&1
   ```

   Replace `/full/path/to/run-strategy` with the output from the `which run-strategy` command above. Also replace `/path/to/logs/` with the directory where you'd like to store log files (create it if needed).

---

## 🤖 24/7 Automation Mode

The bot now supports **continuous 24/7 operation** with built-in market hours awareness! Instead of relying on cron jobs, you can run the bot continuously and it will automatically:

- ✅ **Monitor market hours** and only execute during trading hours
- ✅ **Skip weekends and holidays** automatically  
- ✅ **Send Discord notifications** for all activities
- ✅ **Handle errors gracefully** and continue running
- ✅ **Respect daily execution limits** to prevent over-trading

### Quick Start - Continuous Mode

```bash
# Start the bot in 24/7 continuous mode
run-strategy --continuous

# With custom settings (check every 30 minutes, max 2 executions per day)
run-strategy --continuous --check-interval 30 --max-runs-per-day 2
```

### New Command Line Options

- `--continuous` — Enable 24/7 continuous mode with market hours awareness
- `--check-interval N` — Check market status every N minutes (default: 15)
- `--max-runs-per-day N` — Maximum strategy executions per trading day (default: 4)
- `--test-market-hours` — Test market hours checker and exit

### How It Works

1. **Continuous Monitoring**: Checks market status every 15 minutes (configurable)
2. **Smart Execution**: Only executes trades during regular market hours (9:30 AM - 4:00 PM ET)
3. **Daily Limits**: Prevents over-trading with configurable daily execution limits
4. **Market Hours Validation**: Automatically handles weekends, holidays, and pre/after-market hours
5. **Discord Integration**: Sends notifications for all scheduler events

### Example Usage

```bash
# Conservative: Check hourly, execute once per day
run-strategy --continuous --check-interval 60 --max-runs-per-day 1

# Active: Check every 15 minutes, execute up to 4 times per day  
run-strategy --continuous --check-interval 15 --max-runs-per-day 4

# With full logging for monitoring
run-strategy --continuous --strat-log --log-to-file --log-level INFO
```

### Market Hours Information

- **Regular Trading**: 9:30 AM - 4:00 PM ET, Monday-Friday
- **Options Trading**: Only available during regular market hours
- **Holiday Aware**: Automatically recognizes US market holidays
- **Timezone Safe**: Handles Eastern Time conversions and daylight saving

### Benefits Over Cron Jobs

- **No missed executions** due to market closures
- **Real-time market hours validation**
- **Built-in error recovery and retry logic**
- **Comprehensive Discord notifications**
- **No complex cron scheduling needed**

📖 **For detailed setup instructions, see [AUTOMATION_GUIDE.md](./AUTOMATION_GUIDE.md)**

---

## Manual Automation (Alternative)

If you prefer traditional cron job scheduling instead of continuous mode:

1. **Follow the cron job setup instructions above.**
2. **Remove any existing cron jobs** for `run-strategy` to avoid conflicts with continuous mode.
3. **Monitor your email or Discord** for notifications about strategy execution and errors.

---

## Test Results

To validate the code mechanics, the strategy was tested in an Alpaca paper account over the course of two weeks (May 14 – May 28, 2025). A full report and explanation of each decision point can be found in [`reports/options-wheel-strategy-test.pdf`](./reports/options-wheel-strategy-test.pdf). A high-level summary of the trading results is given below.

### Premiums Collected

| Underlying | Expiry     | Strike | Type | Date Sold  | Premium Collected |
| ---------- | ---------- | ------ | ---- | ---------- | ----------------- |
| PLTR       | 2025-05-23 | 124    | P    | 2025-05-14 | \$261.00          |
| NVDA       | 2025-05-30 | 127    | P    | 2025-05-14 | \$332.00          |
| MP         | 2025-05-23 | 20     | P    | 2025-05-14 | \$28.00           |
| AAL        | 2025-05-30 | 11     | P    | 2025-05-14 | \$20.00           |
| INTC       | 2025-05-30 | 20.50  | P    | 2025-05-14 | \$33.00           |
| CAT        | 2025-05-16 | 345    | P    | 2025-05-14 | \$140.00          |
| AAPL       | 2025-05-23 | 200    | P    | 2025-05-19 | \$110.00          |
| DLR        | 2025-05-30 | 165    | P    | 2025-05-20 | \$67.00           |
| AAPL       | 2025-05-30 | 202.50 | C    | 2025-05-27 | \$110.00          |
| MP         | 2025-05-30 | 20.50  | C    | 2025-05-27 | \$12.00           |
| PLTR       | 2025-05-30 | 132    | C    | 2025-05-27 | \$127.00          |

**Total Premiums Collected:** **\$1,240.00**

---

### Total PnL (Change in Account Liquidating Value)

| Metric                   | Value           |
| ------------------------ | --------------- |
| Starting Balance         | \$100,000.00    |
| Ending Balance           | \$100,951.89    |
| Net PnL                  | **+\$951.89** |

---

### Disclaimer

These results are based on historical, simulated trading in a paper account over a limited timeframe and **do not represent actual live trading performance**. They are provided solely to demonstrate the mechanics of the strategy and its ability to automate the Wheel process in a controlled environment. **Past performance is not indicative of future results.** Trading in live markets involves risk, and there is no guarantee that future performance will match these simulated results.

---

## Core Strategy Logic

The core logic is defined in `core/strategy.py`.

* **Stock Filtering:**
  The strategy filters underlying stocks based on available buying power. It fetches the latest trade prices for each candidate symbol and retains only those where the cost to buy 100 shares (`price × 100`) is within your buying power limit. This keeps trades within capital constraints and can be extended to include custom filters like volatility or technical indicators.

* **Option Filtering:**
  Put options are filtered by absolute delta, which must lie between `DELTA_MIN` and `DELTA_MAX`, by open interest (`OPEN_INTEREST_MIN`) to ensure liquidity, and by yield (between `YIELD_MIN` and `YIELD_MAX`). For short calls, the strategy applies a minimum strike price filter (`min_strike`) to ensure the strike is above the underlying purchase price. This helps avoid immediate assignment and locks in profit if the call is assigned.

* **Option Scoring:**
  Options are scored to estimate their attractiveness based on annualized return, adjusted for assignment risk. The score formula is:

   `score = (1 - |Δ|) × (250 / (DTE + 5)) × (bid price / strike price)`

  Where:

  * $\Delta$ = option delta (a rough proxy for the probability of assignment)
  * DTE = days to expiration
  * The factor 250 approximates the number of trading days in a year
  * Adding 5 days to DTE smooths the score for near-term options

* **Option Selection:**
  From all scored options, the strategy picks the highest-scoring contract per underlying symbol to promote diversification. It filters out options scoring below `SCORE_MIN` and returns either the top N options or all qualifying options.

---

## Ideas for Customization

### Stock Picking

* Use technical indicators such as moving averages, RSI, or support/resistance levels to identify stocks likely to remain range-bound — ideal for selling options in the Wheel strategy.
* Incorporate fundamental filters like earnings growth, dividend history, or volatility to select stocks you’re comfortable holding long term.

### Scoring Function for Puts / Calls

* Modify the scoring formula to weight factors differently or separately for puts vs calls. For example, emphasize calls with strikes just below resistance levels or puts on stocks with strong support.
* Consider adding factors like implied volatility or premium decay to better capture option pricing nuances.

### Managing a Larger Portfolio

* Allocate larger trade sizes to higher-scoring options for more efficient capital use.
* Allow multiple wheels per stock to increase position flexibility.
* Set exposure limits per underlying or sector to manage risk.

### Stop Loss When Puts Get Assigned

* Implement logic to cut losses if a stock price falls sharply after assignment, protecting capital from downside.

### Rolling Short Puts as Expiration Nears

* Instead of letting puts expire or get assigned, roll them forward to the next expiration or down to lower strikes to capture additional premium and manage risk.
* (For more, see [this Learn article](https://alpaca.markets/learn/options-wheel-strategy).)

---

## Final Notes

This is a great starting point for automating your trading, but always double-check your live trades — no system is completely hands-off.

Happy wheeling! 🚀

---
<div style="font-size: 0.8em;">
Disclosures

Options trading is not suitable for all investors due to its inherent high risk, which can potentially result in significant losses. Please read [Characteristics and Risks of Standardized Options](https://www.theocc.com/company-information/documents-and-archives/options-disclosure-document) before investing in options

The Paper Trading API is offered by AlpacaDB, Inc. and does not require real money or permit a user to transact in real securities in the market. Providing use of the Paper Trading API is not an offer or solicitation to buy or sell securities, securities derivative or futures products of any kind, or any type of trading or investment advice, recommendation or strategy, given or in any manner endorsed by AlpacaDB, Inc. or any AlpacaDB, Inc. affiliate and the information made available through the Paper Trading API is not an offer or solicitation of any kind in any jurisdiction where AlpacaDB, Inc. or any AlpacaDB, Inc. affiliate (collectively, “Alpaca”) is not authorized to do business.

All investments involve risk, and the past performance of a security, or financial product does not guarantee future results or returns. There is no guarantee that any investment strategy will achieve its objectives. Please note that diversification does not ensure a profit, or protect against loss. There is always the potential of losing money when you invest in securities, or other financial products. Investors should consider their investment objectives and risks carefully before investing.

Please note that this article is for general informational purposes only and is believed to be accurate as of the posting date but may be subject to change. The examples above are for illustrative purposes only and should not be considered investment advice. 

Securities brokerage services are provided by Alpaca Securities LLC ("Alpaca Securities"), member [FINRA](https://www.finra.org/)/[SIPC](https://www.sipc.org/), a wholly-owned subsidiary of AlpacaDB, Inc. Technology and services are offered by AlpacaDB, Inc.

This is not an offer, solicitation of an offer, or advice to buy or sell securities or open a brokerage account in any jurisdiction where Alpaca Securities is not registered or licensed, as applicable.
</div>
