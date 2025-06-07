# Discord Webhook Setup Guide

This guide will help you set up Discord notifications for your Options Wheel Strategy bot.

## Step 1: Create a Discord Webhook

1. **Open Discord** and go to the server where you want to receive notifications
2. **Click on the server name** at the top left, then select "Server Settings"
3. **Go to "Integrations"** in the left sidebar
4. **Click "Webhooks"** in the integrations menu
5. **Click "New Webhook"**
6. **Configure your webhook:**
   - **Name**: Options Wheel Bot (or any name you prefer)
   - **Channel**: Select the channel where you want notifications
   - **Avatar**: Upload an icon if desired (optional)
7. **Copy the Webhook URL** - you'll need this for your .env file

## Step 2: Configure Your Environment

1. **Open your .env file** in the project root
2. **Add the Discord configuration:**
   ```env
   # Discord Webhook Configuration
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   DISCORD_NOTIFICATIONS_ENABLED=true
   ```
3. **Replace the webhook URL** with the one you copied from Discord

## Step 3: Test the Integration

1. **Open PowerShell** in your project directory
2. **Activate your virtual environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
3. **Run the Discord test:**
   ```powershell
   run-strategy --test-discord
   ```

You should see output like:
```
Testing Discord webhook functionality...
✅ Discord notifications are enabled
📡 Webhook URL configured: https://discord.com/api/webhooks/123456...
📤 Sending test startup message...
📤 Sending test trade notification...
📤 Sending test completion message...
✅ All test messages sent successfully!
📱 Check your Discord channel to see if the messages appeared.
```

## Step 4: Verify in Discord

Check your Discord channel - you should see three test messages:
1. A startup message (green embed)
2. A trade notification (orange/red embed)
3. A completion message (green embed)

## Troubleshooting

### "Discord notifications are disabled or not configured"
- Make sure your .env file has both `DISCORD_WEBHOOK_URL` and `DISCORD_NOTIFICATIONS_ENABLED=true`
- Check that there are no typos in your environment variable names
- Restart your terminal and try again

### "Error sending Discord messages"
- Verify your webhook URL is correct
- Make sure the Discord server and channel still exist
- Check that the webhook hasn't been deleted from Discord
- Test your internet connection

### Messages not appearing in Discord
- Check you're looking at the correct channel
- Verify the webhook is configured for the right channel
- Try regenerating the webhook URL in Discord

## Message Types

Once configured, your bot will automatically send notifications for:

- **🚀 Bot Started**: When the strategy begins execution
- **📈 Put Sold / 📉 Call Sold**: When options contracts are sold
- **📊 Position Updates**: Current portfolio status
- **✅ Execution Complete**: When the strategy finishes running
- **❌ Errors**: If any errors occur during execution

## Disabling Notifications

To temporarily disable Discord notifications without removing the webhook:
```env
DISCORD_NOTIFICATIONS_ENABLED=false
```

To permanently disable, simply remove or comment out the Discord lines in your .env file.
