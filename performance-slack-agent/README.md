# Performance Slack Agent

Automated agent that monitors daily performance metrics from Mode Analytics and posts celebration GIFs to Slack when yesterday's performance beats the forecast.

## Features

- Fetches yesterday's performance data from Mode Analytics
- Compares actual performance against forecast
- Selects celebration GIFs using Giphy API (with fallback GIFs)
- Interactive review workflow before posting
- Posts rich formatted messages to Slack with GIFs
- Configurable performance thresholds
- Auto-post mode for full automation

## Setup

### 1. Install Dependencies

From the repository root:
```bash
pip install -r requirements.txt
```

### 2. Configure API Access

#### Mode Analytics
1. Get your Mode API credentials from [Mode Settings > API Tokens](https://mode.com/settings/api)
2. Note your workspace name and report ID from the Mode dashboard URL

#### Slack
1. Create a Slack App at [api.slack.com/apps](https://api.slack.com/apps)
2. Add the following OAuth scopes under "OAuth & Permissions":
   - `chat:write` - Post messages
   - `chat:write.public` - Post to public channels
3. Install the app to your workspace
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
5. Get your channel ID by right-clicking on the channel > View channel details

#### Giphy (Optional)
1. Get a free API key from [developers.giphy.com](https://developers.giphy.com/)
2. If not provided, agent will use fallback celebration GIFs

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp ../.env.example ../.env
```

Edit `.env` with your credentials:
```bash
# Mode Analytics
MODE_API_TOKEN=your_mode_api_token
MODE_API_SECRET=your_mode_api_secret
MODE_WORKSPACE=your_workspace_name
MODE_REPORT_ID=your_report_id

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C1234567890

# Giphy (optional)
GIPHY_API_KEY=your_giphy_api_key

# Performance threshold
PERFORMANCE_THRESHOLD=0.0
```

### 4. Configure Agent Settings

Edit `config.yaml` to customize:
- Mode report settings (field names for actual/forecast)
- Performance threshold (minimum % to beat forecast)
- GIF search query
- Custom message template

## Usage

### Interactive Mode (with Review)

Run the agent and review the GIF before posting:

```bash
cd performance-slack-agent
python agent.py
```

The agent will:
1. Fetch yesterday's performance from Mode
2. Display performance vs forecast
3. If forecast was beaten, select a celebration GIF
4. Show you the GIF URL for review
5. Ask for confirmation before posting to Slack

### Auto-Post Mode

Skip the review and automatically post:

```bash
python agent.py --auto-post
```

### Test Slack Connection

Verify your Slack credentials are working:

```bash
python agent.py --test-slack
```

### Custom Configuration File

Use a different config file:

```bash
python agent.py --config /path/to/custom-config.yaml
```

## Automation

### Daily Scheduled Run

Add to your crontab to run daily at 9 AM:

```bash
0 9 * * * cd /path/to/agents/performance-slack-agent && python agent.py --auto-post
```

### CI/CD Integration

Run as part of your CI/CD pipeline:

```bash
# Example GitHub Actions
- name: Check Performance
  run: |
    cd performance-slack-agent
    python agent.py --auto-post
  env:
    MODE_API_TOKEN: ${{ secrets.MODE_API_TOKEN }}
    MODE_API_SECRET: ${{ secrets.MODE_API_SECRET }}
    SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

## Configuration Options

### Performance Threshold

Control when celebrations are posted:

```yaml
threshold: 5.0  # Only celebrate if beat forecast by 5% or more
```

### Custom Messages

Customize the Slack message format:

```yaml
message:
  template: |
    🔥 We're on fire! 🔥

    Actual: {actual:,.2f}
    Forecast: {forecast:,.2f}
    Crushed it by: {beat_percentage:.1f}%
```

### GIF Search Queries

Customize what types of GIFs are selected:

```yaml
gif:
  search_query: "office celebration dance party"
```

## Mode Report Requirements

Your Mode report should contain at least these columns:
- `actual` - Yesterday's actual performance
- `forecast` - Yesterday's forecasted performance

The agent fetches the most recent row from your report. Ensure your Mode report:
1. Filters to yesterday's date
2. Orders by date (most recent last)
3. Contains the actual and forecast columns

You can customize the column names in `config.yaml`:

```yaml
mode:
  performance_field: "daily_revenue"
  forecast_field: "revenue_forecast"
```

## Troubleshooting

### "No runs found for report"
- Ensure your Mode report has been run recently
- Check that the report ID in your config is correct

### "Slack connection failed"
- Verify your bot token is correct
- Ensure the bot has been added to the target channel
- Check that required OAuth scopes are enabled

### "No GIFs found"
- If using Giphy, check your API key is valid
- Agent will fall back to default GIFs if Giphy fails

### "Could not parse performance data"
- Verify the field names in config.yaml match your Mode report columns
- Ensure your Mode report returns numeric values

## Logs

The agent writes detailed logs to `agent.log` in the same directory. Check this file for debugging.

## Example Output

```
┌─────────────────────────────────────┐
│ Performance Slack Agent             │
│ Run time: 2026-01-11 09:00:00      │
└─────────────────────────────────────┘

Checking yesterday's performance...

        Performance Results
┌──────────────┬──────────────────┐
│ Metric       │ Value            │
├──────────────┼──────────────────┤
│ Actual       │ 125,430.50       │
│ Forecast     │ 120,000.00       │
│ Beat Forecast? │ ✓ Yes          │
│ Beat By      │ 4.53%            │
└──────────────┴──────────────────┘

Selecting celebration GIF...
Selected: Celebration Success GIF

Review
GIF URL: https://media.giphy.com/media/xyz/giphy.gif

This will post to Slack channel: C1234567890

Do you want to post this to Slack? [Y/n]: y

Posting to Slack...
✓ Posted to Slack successfully!
```

## License

MIT
