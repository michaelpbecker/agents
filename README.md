# Professional Workflow Agents

A collection of intelligent agents for automating professional workflows.

## Agents

### 🎉 Performance Celebration Slack Bot

Native Slack bot that monitors MTD performance metrics from Mode Analytics and facilitates team celebrations when you beat your finance forecast.

**Key Features:**
- `/check-performance` slash command to check current metrics
- Interactive button-driven workflow
- Native Slack `/giphy` integration for GIF selection
- Review before posting to ensure quality control
- Tracks MTD vs Finance Forecast metrics automatically

**Quick Start:**
```bash
cd performance-slack-agent
pip install -r ../requirements.txt
python slack_bot.py
```

See [performance-slack-agent/README.md](performance-slack-agent/README.md) for complete setup instructions.

**Workflow:**
1. Run `/check-performance` in Slack
2. Bot shows MTD performance (only visible to you)
3. If beating forecast, click "Post Celebration" button
4. Add a GIF using `/giphy`, paste the URL
5. Customize message and post to channel!

---

## Project Structure

```
agents/
├── README.md                          # This file
├── requirements.txt                   # Shared Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                        # Git ignore rules
│
├── shared/                           # Shared libraries for all agents
│   ├── __init__.py                   # Package init
│   ├── mode_client.py                # Mode Analytics API client
│   ├── slack_utils.py                # Slack utilities and helpers
│   └── config.py                     # Configuration management
│
├── agent-template/                   # Template for creating new agents
│   ├── README.md                     # Template documentation
│   ├── agent.py                      # Template agent code
│   └── .env.example                  # Template environment variables
│
└── performance-slack-agent/          # Performance celebration bot
    ├── README.md                      # Agent documentation
    ├── slack_bot.py                   # Main Slack bot (Socket Mode)
    ├── mode_client.py                 # Mode client (legacy, use shared/)
    ├── slack_client.py                # Slack helpers (legacy, use shared/)
    ├── agent.py                       # CLI agent (legacy)
    ├── config.yaml                    # Configuration
    └── gif_selector.py                # GIF selection (legacy)
```

## Setup

### 1. Install Dependencies

All agents share common dependencies:

```bash
pip install -r requirements.txt
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials and settings. Each agent may require different environment variables.

### 3. Run Your Agent

Follow the specific README in each agent's directory for detailed setup and usage instructions.

## Development

### Adding a New Agent

Creating a new agent is easy using the provided template:

1. **Copy the agent template**:
   ```bash
   cp -r agent-template your-new-agent-name
   cd your-new-agent-name
   ```

2. **Customize the agent**:
   - Edit `agent.py` with your logic
   - Update `README.md` with documentation
   - Add environment variables to root `.env`

3. **Use shared libraries** instead of duplicating code:
   ```python
   from shared.mode_client import ModeClient
   from shared.slack_utils import get_slack_client, post_message
   from shared.config import load_env_file, setup_logging
   ```

4. **Update main README** (this file) with your agent description

5. **Test thoroughly** before committing

📚 **New to creating agents?** See [ADDING_AGENTS.md](ADDING_AGENTS.md) for a complete step-by-step tutorial with examples.

See [agent-template/README.md](agent-template/README.md) for detailed template documentation.

### Shared Libraries

All agents can use these shared modules (in `shared/`):

**`shared.mode_client`**
- `ModeClient` - Mode Analytics API integration
- Methods for fetching reports and performance data

**`shared.slack_utils`**
- `get_slack_client()` - Get configured Slack client
- `post_message()`, `post_ephemeral()` - Send messages
- Block helpers: `create_section_block()`, `create_button()`, etc.
- Formatting: `format_user_mention()`, `format_link()`, etc.

**`shared.config`**
- `load_env_file()` - Load environment variables
- `setup_logging()` - Configure logging
- `validate_required_env_vars()` - Validate configuration
- `Config` class for YAML + env configuration

### Best Practices

- **Reuse shared libraries** - Don't duplicate Mode, Slack, or config code
- **Keep agents modular** - One agent, one purpose
- **Document everything** - Update README with setup instructions
- **Use environment variables** - Never hardcode secrets
- **Add logging** - Use `shared.config.setup_logging()`
- **Handle errors** - Catch and log exceptions appropriately
- **Type hints** - Makes code more maintainable
- **Follow PEP 8** - Consistent Python style

## Common Dependencies

- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `slack-sdk` / `slack-bolt` - Slack integration
- `pyyaml` - YAML configuration parsing
- `rich` - Terminal formatting (for CLI agents)

## Environment Variables

See `.env.example` for all available configuration options. Common variables:

```bash
# Mode Analytics
MODE_API_TOKEN=your_token
MODE_API_SECRET=your_secret
MODE_WORKSPACE=workspace_name
MODE_REPORT_ID=report_id

# Slack
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_SIGNING_SECRET=your_secret
```

## Contributing

When adding new features or agents:

1. Test thoroughly before committing
2. Update documentation
3. Add configuration examples
4. Include error handling
5. Write clear commit messages

## License

MIT

## Support

For issues or questions about specific agents, see their individual README files.
