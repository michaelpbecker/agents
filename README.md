# Professional Workflow Agents

A collection of automation agents for professional workflows.

## Agents

### Performance Slack Agent

Automated agent that monitors daily performance metrics against forecasts and posts celebration GIFs to Slack when targets are exceeded.

**Features:**
- Fetches performance data from Mode Analytics
- Compares yesterday's performance against forecast
- Selects celebration GIFs when performance exceeds forecast
- Review workflow before posting to Slack
- Configurable thresholds and Slack channels

See [performance-slack-agent/README.md](./performance-slack-agent/README.md) for details.

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your API keys
4. Navigate to the specific agent directory for usage instructions

## Requirements

- Python 3.8+
- API access to Mode Analytics
- Slack workspace with bot permissions
- Giphy API key (optional, for GIF selection)
