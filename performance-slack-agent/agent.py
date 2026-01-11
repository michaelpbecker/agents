#!/usr/bin/env python3
"""
Performance Slack Agent

Monitors daily performance metrics against forecasts and posts celebration
GIFs to Slack when targets are exceeded.

Usage:
    python agent.py [--auto-post] [--config config.yaml]

Options:
    --auto-post: Skip review and automatically post if forecast is beaten
    --config: Path to configuration file (default: config.yaml)
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.markdown import Markdown
import yaml

from mode_client import ModeClient
from slack_client import SlackClient
from gif_selector import GifSelector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
console = Console()


class PerformanceSlackAgent:
    """Agent that monitors performance and posts celebrations to Slack."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            config_path: Path to configuration file
        """
        # Load environment variables
        load_dotenv()

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize clients
        self.mode_client = ModeClient()
        self.slack_client = SlackClient()
        self.gif_selector = GifSelector()

        logger.info("Performance Slack Agent initialized")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent / 'config.yaml'
        else:
            config_path = Path(config_path)

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        else:
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return {
                'mode': {
                    'report_id': os.getenv('MODE_REPORT_ID'),
                    'performance_field': 'actual',
                    'forecast_field': 'forecast'
                },
                'threshold': float(os.getenv('PERFORMANCE_THRESHOLD', '0.0')),
                'gif': {
                    'search_query': 'celebration success winner'
                },
                'message': {
                    'template': None  # Use default
                }
            }

    def check_performance(self) -> Dict[str, Any]:
        """
        Check yesterday's performance against forecast.

        Returns:
            Dictionary with performance data
        """
        console.print("\n[bold blue]Checking yesterday's performance...[/bold blue]")

        report_id = self.config['mode']['report_id']
        performance_field = self.config['mode'].get('performance_field', 'actual')
        forecast_field = self.config['mode'].get('forecast_field', 'forecast')

        performance_data = self.mode_client.get_yesterday_performance(
            report_id=report_id,
            performance_field=performance_field,
            forecast_field=forecast_field
        )

        # Create a nice table to display results
        table = Table(title="Performance Results")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Actual", f"{performance_data['actual']:,.2f}")
        table.add_row("Forecast", f"{performance_data['forecast']:,.2f}")
        table.add_row("Beat Forecast?", "✓ Yes" if performance_data['beat_forecast'] else "✗ No")
        table.add_row("Beat By", f"{performance_data['beat_percentage']:.2f}%")

        console.print(table)

        return performance_data

    def select_gif(self) -> Dict[str, str]:
        """
        Select a celebration GIF.

        Returns:
            Dictionary with 'url' and 'title' keys
        """
        console.print("\n[bold blue]Selecting celebration GIF...[/bold blue]")

        search_query = self.config.get('gif', {}).get('search_query', 'celebration success')
        gif = self.gif_selector.get_random_celebration_gif(query=search_query)

        console.print(f"[green]Selected:[/green] {gif['title']}")
        console.print(f"[dim]{gif['url']}[/dim]")

        return gif

    def review_and_post(self, performance_data: Dict[str, Any],
                       gif: Dict[str, str], auto_post: bool = False) -> bool:
        """
        Review the GIF and post to Slack.

        Args:
            performance_data: Performance data dictionary
            gif: GIF data dictionary
            auto_post: If True, skip review and post automatically

        Returns:
            True if posted, False otherwise
        """
        if not auto_post:
            console.print("\n[bold yellow]Review[/bold yellow]")
            console.print(f"GIF URL: {gif['url']}")
            console.print(f"\nThis will post to Slack channel: {os.getenv('SLACK_CHANNEL_ID')}")

            # Ask for confirmation
            should_post = Confirm.ask("\nDo you want to post this to Slack?", default=True)

            if not should_post:
                console.print("[yellow]Posting cancelled.[/yellow]")
                return False

        # Post to Slack
        console.print("\n[bold blue]Posting to Slack...[/bold blue]")

        custom_message = self.config.get('message', {}).get('template')
        if custom_message:
            # Replace placeholders in custom message
            custom_message = custom_message.format(
                actual=performance_data['actual'],
                forecast=performance_data['forecast'],
                beat_percentage=performance_data['beat_percentage']
            )

        self.slack_client.post_celebration_message(
            gif_url=gif['url'],
            actual=performance_data['actual'],
            forecast=performance_data['forecast'],
            beat_percentage=performance_data['beat_percentage'],
            custom_message=custom_message
        )

        console.print("[bold green]✓ Posted to Slack successfully![/bold green]")
        return True

    def run(self, auto_post: bool = False) -> None:
        """
        Run the agent workflow.

        Args:
            auto_post: If True, skip review and post automatically
        """
        try:
            # Display header
            console.print(Panel.fit(
                "[bold cyan]Performance Slack Agent[/bold cyan]\n"
                f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                border_style="blue"
            ))

            # Step 1: Check performance
            performance_data = self.check_performance()

            # Check if we beat the forecast
            threshold = self.config.get('threshold', 0.0)
            if not performance_data['beat_forecast']:
                console.print("\n[yellow]Performance did not beat forecast. No celebration today.[/yellow]")
                return

            if performance_data['beat_percentage'] < threshold:
                console.print(
                    f"\n[yellow]Performance beat forecast by {performance_data['beat_percentage']:.2f}%, "
                    f"but threshold is {threshold}%. No celebration today.[/yellow]"
                )
                return

            # Step 2: Select GIF
            gif = self.select_gif()

            # Step 3: Review and post
            self.review_and_post(performance_data, gif, auto_post=auto_post)

        except Exception as e:
            logger.error(f"Error running agent: {e}", exc_info=True)
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Performance Slack Agent')
    parser.add_argument('--auto-post', action='store_true',
                       help='Skip review and automatically post if forecast is beaten')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')
    parser.add_argument('--test-slack', action='store_true',
                       help='Test Slack connection and exit')

    args = parser.parse_args()

    # Create and run agent
    agent = PerformanceSlackAgent(config_path=args.config)

    if args.test_slack:
        console.print("[bold blue]Testing Slack connection...[/bold blue]")
        if agent.slack_client.test_connection():
            console.print("[bold green]✓ Slack connection successful![/bold green]")
            try:
                channel_info = agent.slack_client.get_channel_info()
                console.print(f"Channel: #{channel_info.get('name', 'unknown')}")
            except Exception as e:
                console.print(f"[yellow]Could not get channel info: {e}[/yellow]")
        else:
            console.print("[bold red]✗ Slack connection failed[/bold red]")
        sys.exit(0)

    agent.run(auto_post=args.auto_post)


if __name__ == '__main__':
    main()
