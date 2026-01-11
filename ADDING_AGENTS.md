# Adding New Agents - Quick Start Guide

This guide shows you exactly how to add a new agent to this repository in **5 minutes**.

## Example: Create a "Daily Summary" Agent

Let's create an agent that sends a daily summary email. This example shows the complete workflow.

### Step 1: Copy the Template (30 seconds)

```bash
# From the agents/ directory
cp -r agent-template daily-summary-agent
cd daily-summary-agent
```

### Step 2: Update the Agent Code (2 minutes)

Edit `agent.py`:

```python
#!/usr/bin/env python3
"""
Daily Summary Agent

Sends a daily summary of key metrics via email.
"""

import os
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared utilities
from shared.config import load_env_file, setup_logging, validate_required_env_vars
from shared.mode_client import ModeClient
from shared.slack_utils import get_slack_client, post_message

# Load environment and logging
load_env_file()
setup_logging(log_file='daily-summary.log', log_level='INFO')

logger = logging.getLogger(__name__)


class DailySummaryAgent:
    """Sends daily summary of metrics."""

    def __init__(self):
        self.mode_client = ModeClient()
        self.slack_client = get_slack_client()

    def run(self):
        """Main execution."""
        logger.info("Generating daily summary...")

        # Fetch data
        report_id = os.getenv('MODE_REPORT_ID')
        data = self.mode_client.fetch_report_data(report_id)

        # Build summary
        summary = self.build_summary(data)

        # Send to Slack
        channel = os.getenv('SLACK_CHANNEL_ID')
        post_message(
            self.slack_client,
            channel=channel,
            text=f"Daily Summary:\n{summary}"
        )

        logger.info("Daily summary sent!")

    def build_summary(self, data):
        """Build summary text from data."""
        # Your logic here
        return "Summary of today's metrics..."


def main():
    """Entry point."""
    logger.info("Starting Daily Summary Agent...")

    required_vars = [
        'MODE_API_TOKEN',
        'MODE_API_SECRET',
        'MODE_WORKSPACE',
        'MODE_REPORT_ID',
        'SLACK_BOT_TOKEN',
        'SLACK_CHANNEL_ID'
    ]

    if validate_required_env_vars(required_vars):
        sys.exit(1)

    agent = DailySummaryAgent()
    agent.run()


if __name__ == "__main__":
    main()
```

### Step 3: Update Documentation (1 minute)

Edit `README.md`:

```markdown
# Daily Summary Agent

Sends a daily summary of key metrics to Slack.

## Features

- Fetches daily metrics from Mode Analytics
- Formats a summary message
- Posts to Slack channel

## Setup

1. Configure environment variables in root `.env`:
   ```bash
   MODE_API_TOKEN=your_token
   MODE_API_SECRET=your_secret
   MODE_WORKSPACE=workspace
   MODE_REPORT_ID=report_id
   SLACK_BOT_TOKEN=xoxb-token
   SLACK_CHANNEL_ID=C123456
   ```

2. Run the agent:
   ```bash
   python agent.py
   ```

3. (Optional) Schedule with cron:
   ```bash
   0 9 * * * cd /path/to/agents/daily-summary-agent && python agent.py
   ```

## Configuration

Customize the summary format by editing the `build_summary()` method.
```

### Step 4: Add Environment Variables (30 seconds)

Add to root `.env` file:

```bash
# Daily Summary Agent
# (Uses shared MODE and SLACK variables)
```

### Step 5: Update Main README (30 seconds)

Edit `agents/README.md` and add your agent to the "Agents" section:

```markdown
### 📧 Daily Summary Agent

Sends automated daily summaries of key metrics to Slack.

**Quick Start:**
```bash
cd daily-summary-agent
python agent.py
```

See [daily-summary-agent/README.md](daily-summary-agent/README.md) for details.
```

### Step 6: Test It! (30 seconds)

```bash
# Make sure you're in the agent directory
cd daily-summary-agent

# Run it
python agent.py
```

Done! You've created a new agent in 5 minutes. 🎉

---

## Available Shared Libraries

Don't reinvent the wheel - use these shared modules:

### Mode Analytics Integration

```python
from shared.mode_client import ModeClient

client = ModeClient()
data = client.fetch_report_data(report_id='abc123')
performance = client.get_finance_forecast_performance(report_id='abc123')
```

### Slack Integration

```python
from shared.slack_utils import (
    get_slack_client,
    post_message,
    post_ephemeral,
    create_section_block,
    create_button
)

client = get_slack_client()
post_message(client, channel='C123', text='Hello!')

# Or build rich messages
blocks = [
    create_section_block("*Header*", fields=["Field 1", "Field 2"]),
    create_image_block("https://example.com/image.gif")
]
post_message(client, channel='C123', text='Fallback', blocks=blocks)
```

### Configuration & Logging

```python
from shared.config import (
    load_env_file,
    setup_logging,
    validate_required_env_vars,
    Config
)

# Load .env
load_env_file()

# Setup logging
setup_logging(log_file='my-agent.log', log_level='INFO')

# Validate environment variables
required = ['API_KEY', 'SLACK_TOKEN']
missing = validate_required_env_vars(required)
if missing:
    sys.exit(1)

# Load YAML config (optional)
config = Config(yaml_path=Path('config.yaml'))
value = config.get('my.nested.key', default='default_value')
```

---

## Common Agent Patterns

### Pattern 1: Slack Bot with Commands

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

@app.command("/my-command")
def handle_command(ack, command, client):
    ack()
    # Your logic here
    client.chat_postMessage(
        channel=command['channel_id'],
        text="Response"
    )

def main():
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

### Pattern 2: Scheduled Data Fetcher

```python
from shared.mode_client import ModeClient
from shared.slack_utils import get_slack_client, post_message

def main():
    # Fetch data
    mode = ModeClient()
    data = mode.fetch_report_data(os.getenv('MODE_REPORT_ID'))

    # Process
    result = process_data(data)

    # Send to Slack
    slack = get_slack_client()
    post_message(slack, channel=os.getenv('SLACK_CHANNEL_ID'), text=result)
```

### Pattern 3: Interactive Workflow

```python
@app.action("button_click")
def handle_button(ack, body, client):
    ack()

    # Open modal
    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "callback_id": "my_modal",
            "title": {"type": "plain_text", "text": "My Modal"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [...]
        }
    )

@app.view("my_modal")
def handle_submission(ack, body, client, view):
    ack()
    # Process modal submission
```

---

## Tips

1. **Start with the template** - It has all the boilerplate
2. **Import from `shared/`** - Don't duplicate code
3. **Use environment variables** - Never hardcode secrets
4. **Add logging** - Makes debugging easier
5. **Update READMEs** - Help your future self
6. **Test before committing** - Save time later

## Need Help?

- Check [agent-template/README.md](agent-template/README.md) for detailed docs
- Look at [performance-slack-agent/](performance-slack-agent/) for a complete example
- See [README.md](README.md) for shared library documentation

Happy building! 🚀
