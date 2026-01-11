# Performance Celebration Slack Bot

A native Slack bot that monitors MTD performance metrics from Mode Analytics and facilitates celebration posts when you beat your finance forecast. Uses Slack's interactive features and native `/giphy` command for a seamless workflow.

## Features

- **Slash Command**: `/check-performance` to check current MTD performance
- **Interactive Workflow**: Button-driven celebration posting
- **Native GIF Integration**: Use Slack's `/giphy` command for GIF selection
- **Mode Analytics Integration**: Fetches MTD vs Forecast metrics automatically
- **Rich Formatting**: Beautiful formatted messages with performance details
- **Review Before Posting**: Preview and customize before sharing with the team

## How It Works

1. **Check Performance**: Run `/check-performance` in any Slack channel
2. **Review Results**: Bot shows MTD performance vs forecast (only visible to you)
3. **Celebrate**: If beating forecast, click "Post Celebration" button
4. **Add GIF**: Use `/giphy celebration` to find a GIF, copy the URL
5. **Post**: Paste GIF URL in the modal and post to the channel!

## Dashboard Metrics

The bot tracks these metrics from your Mode dashboard:
- **Finance Forecast**: Monthly target ($K)
- **MTD Actual**: Current month-to-date performance ($K)
- **MTD % vs Forecast**: Percentage variance
- **MTD $ vs Forecast**: Dollar variance ($K)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch"
3. Name it "Performance Celebration Bot" and select your workspace

#### Configure Bot Token Scopes

Under "OAuth & Permissions", add these Bot Token Scopes:
- `app_mentions:read` - See when bot is mentioned
- `chat:write` - Post messages
- `chat:write.public` - Post to public channels without joining
- `commands` - Use slash commands

#### Enable Socket Mode

1. Go to "Socket Mode" in the left sidebar
2. Enable Socket Mode
3. Give it a token name (e.g., "Main Socket") and generate an **App-Level Token**
   - Scope: `connections:write`
4. Copy the token (starts with `xapp-`)

#### Create Slash Command

1. Go to "Slash Commands" in the left sidebar
2. Click "Create New Command"
3. Set:
   - Command: `/check-performance`
   - Short Description: "Check MTD performance vs forecast"
   - Usage Hint: (leave blank)

#### Enable Events & Interactivity

1. Go to "Interactivity & Shortcuts"
2. Turn on Interactivity (Socket Mode handles the URL automatically)

3. Go to "Event Subscriptions"
4. Enable Events
5. Subscribe to bot events:
   - `app_mention` - When bot is mentioned

#### Install to Workspace

1. Go to "Install App" in the left sidebar
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

#### Get Signing Secret

1. Go to "Basic Information"
2. Copy your **Signing Secret** under "App Credentials"

### 3. Configure Mode Analytics

1. Get your Mode API credentials from [Mode Settings > API Tokens](https://mode.com/settings/api)
2. Note your workspace name from the Mode URL: `https://app.mode.com/{workspace}/...`
3. Find your report ID from the dashboard URL

### 4. Set Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Mode Analytics
MODE_API_TOKEN=your_mode_api_token
MODE_API_SECRET=your_mode_api_secret
MODE_WORKSPACE=your_workspace_name
MODE_REPORT_ID=your_report_id

# Slack Bot Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-level-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CHANNEL_ID=C1234567890

# Performance threshold (optional)
PERFORMANCE_THRESHOLD=0.0  # Only celebrate if beat by this % or more
```

### 5. Mode Report Setup

Your Mode report should return these fields (or similar):
- `FINANCE FORECAST` or `finance_forecast` - Monthly forecast target
- `MTD % vs FORECAST` or `mtd_pct_vs_forecast` - Percentage variance
- `MTD $ vs FORECAST` or `mtd_dollar_vs_forecast` - Dollar variance
- `MTD Actual` or `mtd_actual` - Current MTD (optional, can be calculated)

The bot will attempt to find these fields automatically. If your field names are different, you can modify the `_extract_field` calls in `mode_client.py:153-166`.

## Running the Bot

### Development Mode

Run the bot locally:

```bash
cd performance-slack-agent
python slack_bot.py
```

The bot will start and listen for commands in your Slack workspace.

### Production Deployment

#### Option 1: Background Process (Linux/Mac)

```bash
# Using nohup
nohup python slack_bot.py > bot.log 2>&1 &

# Or using screen
screen -S perf-bot
python slack_bot.py
# Press Ctrl+A then D to detach
```

#### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/performance-bot.service`:

```ini
[Unit]
Description=Performance Celebration Slack Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agents/performance-slack-agent
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python slack_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable performance-bot
sudo systemctl start performance-bot
sudo systemctl status performance-bot
```

#### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY performance-slack-agent/ .

CMD ["python", "slack_bot.py"]
```

Build and run:
```bash
docker build -t performance-bot .
docker run -d --env-file .env --name perf-bot performance-bot
```

#### Option 4: Cloud Hosting

The bot works great on:
- **Heroku**: Add `Procfile` with `worker: python performance-slack-agent/slack_bot.py`
- **Railway**: Auto-detects Python and runs the bot
- **AWS EC2/DigitalOcean**: Use systemd service approach
- **Google Cloud Run / AWS Lambda**: Socket Mode works with persistent connections

## Usage

### Check Performance

In any Slack channel or DM with the bot:
```
/check-performance
```

The bot will respond with current MTD performance (only visible to you):

```
┌─────────────────────────────┐
│    Performance Check        │
└─────────────────────────────┘

📈 MTD Performance vs Forecast

Finance Forecast: $166,400K
MTD Actual: $168,900K
Variance %: +2.10%
Variance $: +$2,500K

✅ Beating Forecast!

🎉 Time to celebrate!
Click the button below to post a celebration message.
```

### Post Celebration

1. Click the **"Post Celebration 🎉"** button
2. A modal opens with performance summary
3. **Find a GIF**:
   - In any Slack channel, type `/giphy celebration` (or any search term)
   - Slack shows GIF results
   - Right-click on your favorite GIF > "Copy Link"
4. **Paste GIF URL** in the modal
5. Optionally customize the message
6. Click **"Post to Channel"**

The bot posts a formatted celebration message to the channel!

### Get Help

Mention the bot with "help":
```
@Performance Bot help
```

## Configuration

### Performance Threshold

Only celebrate when beating forecast by a minimum percentage:

```bash
PERFORMANCE_THRESHOLD=2.0  # Only celebrate if beating by 2% or more
```

### Custom Field Names

If your Mode report uses different column names, edit `mode_client.py:155-162`:

```python
finance_forecast = self._extract_field(latest_row,
    ['YOUR_FORECAST_FIELD', 'forecast'])

mtd_pct_vs_forecast = self._extract_field(latest_row,
    ['YOUR_PCT_FIELD', 'pct_vs_forecast'])
```

## Troubleshooting

### Bot Not Responding to /check-performance

- Verify bot is running: Check logs with `tail -f bot.log`
- Check Slack App Token is correct (xapp-...)
- Ensure Socket Mode is enabled
- Verify slash command is created in Slack App settings

### "Could not parse performance data"

- Check your Mode report is returning data
- Review field names in your Mode report
- Check `bot.log` for "Available fields: ..." message
- Update field name mappings in `mode_client.py`

### Modal Won't Open

- Ensure Interactivity is enabled in Slack App settings
- Check Signing Secret is correct
- Review `bot.log` for error messages

### GIF Not Showing

- GIF URL must be a direct link to .gif file
- Supported: Giphy, Tenor, direct .gif URLs
- Try pasting the GIF URL in a regular Slack message first to test

### Bot Not Posting to Channel

- Verify bot has `chat:write` and `chat:write.public` scopes
- Invite bot to private channels: `/invite @Performance Bot`
- Check bot.log for permission errors

## Architecture

```
User (Slack)
    ↓ /check-performance
Slack Bot (slack_bot.py)
    ↓ fetch performance
Mode Client (mode_client.py)
    ↓ query API
Mode Analytics Dashboard
    ↓ return data
Mode Client
    ↓ parse metrics
Slack Bot
    ↓ show results + button (ephemeral)
User
    ↓ clicks "Post Celebration"
Slack Bot
    ↓ opens modal
User
    ↓ adds GIF URL + custom message
Slack Bot
    ↓ posts to channel
Team Celebrates! 🎉
```

## Files

- `slack_bot.py` - Main bot application with slash commands and interactivity
- `mode_client.py` - Mode Analytics API client
- `slack_client.py` - Slack API client (legacy, kept for reference)
- `agent.py` - Legacy CLI agent (deprecated)
- `config.yaml` - Configuration file (deprecated for bot)
- `gif_selector.py` - Giphy integration (deprecated, using Slack's /giphy)

## Legacy CLI Mode

The original CLI-based agent (`agent.py`) is still available but deprecated. Use the new bot (`slack_bot.py`) for a better experience.

## Security Notes

- Never commit `.env` file to git (already in .gitignore)
- Rotate tokens if accidentally exposed
- Bot only responds to users in your Slack workspace
- Performance data shown ephemerally (only visible to requester)
- Use private channels for sensitive metrics

## Support

Check logs for debugging:
```bash
tail -f bot.log
```

All errors and actions are logged with timestamps.

## License

MIT
