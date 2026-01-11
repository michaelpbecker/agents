# Agent Template

Use this template as a starting point for creating new agents in this repository.

## Quick Start

1. **Copy this directory**:
   ```bash
   cp -r agent-template your-new-agent-name
   cd your-new-agent-name
   ```

2. **Rename files and update code**:
   - Rename `agent.py` if needed
   - Update imports to use shared libraries
   - Customize for your use case

3. **Create agent-specific .env variables** (optional):
   - Add to root `.env` file
   - Or create `.env.example` in your agent directory

4. **Update documentation**:
   - Edit this README with your agent's purpose
   - Add setup instructions
   - Document environment variables

5. **Update main repository README**:
   - Add your agent to the agents list
   - Include key features and quick start

## Agent Structure

### Recommended Files

```
your-agent-name/
├── README.md              # Agent-specific documentation
├── agent.py               # Main agent script
├── .env.example           # Agent-specific env vars (optional)
└── config.yaml            # Agent-specific config (optional)
```

### Using Shared Libraries

Import shared utilities instead of duplicating code:

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import shared modules
from shared.mode_client import ModeClient
from shared.slack_utils import get_slack_client, post_message
from shared.config import load_env_file, setup_logging, Config
```

## Available Shared Modules

### `shared.mode_client`
- `ModeClient` - Mode Analytics API client
- Methods for fetching reports, queries, and performance data

### `shared.slack_utils`
- `get_slack_client()` - Get configured Slack WebClient
- `post_message()` - Post messages to Slack
- `post_ephemeral()` - Post ephemeral messages
- Block creation helpers: `create_section_block()`, `create_button()`, etc.
- Formatting helpers: `format_user_mention()`, `format_link()`, etc.

### `shared.config`
- `load_env_file()` - Load environment variables
- `setup_logging()` - Configure logging
- `validate_required_env_vars()` - Validate required env vars
- `Config` - Configuration container class
- `get_required_env_var()` - Get required env var with error handling

## Example Agent Template

See `agent.py` for a complete example agent structure.

## Environment Variables

Add your agent's required environment variables to the main `.env` file:

```bash
# Your Agent Configuration
YOUR_AGENT_API_KEY=your_key_here
YOUR_AGENT_SETTING=value
```

## Testing Your Agent

1. **Install dependencies**:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp ../.env.example ../.env
   # Edit ../.env with your credentials
   ```

3. **Run your agent**:
   ```bash
   python agent.py
   ```

## Best Practices

1. **Reuse shared libraries** - Don't duplicate Mode, Slack, or config code
2. **Use type hints** - Makes code more maintainable
3. **Add logging** - Use `shared.config.setup_logging()`
4. **Error handling** - Catch and log exceptions appropriately
5. **Document well** - Update README with setup and usage
6. **Environment vars** - Use environment variables for secrets
7. **Modular design** - Keep functions focused and testable

## Common Patterns

### Slack Bot Pattern

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from shared.config import load_env_file, setup_logging, validate_required_env_vars

load_env_file()
setup_logging(log_file='bot.log')

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

@app.command("/your-command")
def handle_command(ack, command, client):
    ack()
    # Your logic here

def main():
    required_vars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', ...]
    if validate_required_env_vars(required_vars):
        sys.exit(1)

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

if __name__ == "__main__":
    main()
```

### CLI Agent Pattern

```python
from shared.mode_client import ModeClient
from shared.config import load_env_file, setup_logging, Config

load_env_file()
setup_logging(log_file='agent.log')

def main():
    config = Config()

    # Your agent logic here
    mode_client = ModeClient()
    data = mode_client.fetch_report_data(...)

    # Process and output
    print(data)

if __name__ == "__main__":
    main()
```

## Adding Dependencies

If your agent needs additional Python packages:

1. Add to `../requirements.txt` (shared dependencies)
2. Or create `requirements.txt` in your agent directory (agent-specific)

## Questions?

See the main repository [README.md](../README.md) or check existing agents for examples.
