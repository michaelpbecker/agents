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
└── performance-slack-agent/
    ├── README.md                      # Agent documentation
    ├── slack_bot.py                   # Main Slack bot (Socket Mode)
    ├── mode_client.py                 # Mode Analytics API client
    ├── slack_client.py                # Slack API helpers (legacy)
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

1. Create a new directory under `agents/`:
   ```bash
   mkdir agents/my-new-agent
   ```

2. Add your agent code and README:
   ```bash
   touch agents/my-new-agent/README.md
   touch agents/my-new-agent/agent.py
   ```

3. Update dependencies in `requirements.txt` if needed

4. Update this README with your agent description

### Best Practices

- Keep agents modular and single-purpose
- Document all environment variables in `.env.example`
- Include comprehensive README with setup instructions
- Add error handling and logging
- Use type hints for better code clarity
- Follow Python PEP 8 style guidelines

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
