#!/usr/bin/env python3
"""
Performance Celebration Slack Bot

Native Slack bot that monitors performance and facilitates celebration posts.

Features:
- /check-performance - Check MTD performance vs forecast
- Interactive workflow for GIF selection using Slack's /giphy
- Preview and approve before posting to channel
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

from mode_client import ModeClient

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Initialize Mode client
mode_client = ModeClient()

# Store performance data temporarily (in production, use Redis or similar)
performance_cache = {}


def format_performance_blocks(performance: Dict[str, Any], include_celebration: bool = False) -> list:
    """
    Format performance data as Slack blocks.

    Args:
        performance: Performance data dictionary
        include_celebration: Whether to include celebration button

    Returns:
        List of Slack block kit blocks
    """
    mtd_actual = performance.get('mtd_actual', 0)
    forecast = performance.get('finance_forecast', 0)
    pct_vs_forecast = performance.get('mtd_pct_vs_forecast', 0)
    dollar_vs_forecast = performance.get('mtd_dollar_vs_forecast', 0)
    beat_forecast = performance.get('beat_forecast', False)

    # Header with emoji based on performance
    if beat_forecast:
        header = ":chart_with_upwards_trend: *MTD Performance vs Forecast*"
        status = ":white_check_mark: *Beating Forecast!*"
    else:
        header = ":chart: *MTD Performance vs Forecast*"
        status = ":red_circle: Below Forecast"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Performance Check"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": header
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Finance Forecast:*\n${forecast:,.0f}K"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*MTD Actual:*\n${mtd_actual:,.0f}K"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Variance %:*\n{pct_vs_forecast:+.2f}%"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Variance $:*\n${dollar_vs_forecast:+,.0f}K"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": status
            }
        }
    ]

    if include_celebration and beat_forecast:
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":tada: *Time to celebrate!*\n\n"
                           "Click the button below to post a celebration message.\n"
                           "You'll be able to add a GIF before posting."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Post Celebration :tada:"
                        },
                        "style": "primary",
                        "action_id": "post_celebration",
                        "value": "celebrate"
                    }
                ]
            }
        ])

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
            }
        ]
    })

    return blocks


@app.command("/check-performance")
def handle_check_performance(ack, command, client):
    """
    Handle /check-performance slash command.

    Fetches performance data and shows results with optional celebration button.
    """
    ack()  # Acknowledge the command request

    user_id = command['user_id']
    channel_id = command['channel_id']

    logger.info(f"Performance check requested by user {user_id}")

    try:
        # Send loading message
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="Checking performance data from Mode... :hourglass:"
        )

        # Fetch performance data
        report_id = os.environ.get('MODE_REPORT_ID')
        if not report_id:
            raise ValueError("MODE_REPORT_ID not configured")

        performance = mode_client.get_finance_forecast_performance(report_id)

        # Cache performance data for this user
        performance_cache[user_id] = performance

        # Get performance threshold
        threshold = float(os.environ.get('PERFORMANCE_THRESHOLD', '0.0'))
        include_celebration = performance['beat_forecast'] and performance['mtd_pct_vs_forecast'] >= threshold

        # Format and send the response
        blocks = format_performance_blocks(performance, include_celebration=include_celebration)

        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="Performance check complete",
            blocks=blocks
        )

        logger.info(
            f"Performance check complete: Beat forecast = {performance['beat_forecast']}, "
            f"Variance = {performance['mtd_pct_vs_forecast']:.2f}%"
        )

    except Exception as e:
        logger.error(f"Error checking performance: {e}", exc_info=True)
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f":x: Error checking performance: {str(e)}"
        )


@app.action("post_celebration")
def handle_post_celebration(ack, body, client):
    """
    Handle "Post Celebration" button click.

    Opens a modal for user to add GIF and post celebration.
    """
    ack()

    user_id = body['user']['id']
    trigger_id = body['trigger_id']

    logger.info(f"Post celebration triggered by user {user_id}")

    # Get cached performance data
    performance = performance_cache.get(user_id)
    if not performance:
        logger.warning(f"No cached performance data for user {user_id}")
        # Fetch fresh data
        try:
            report_id = os.environ.get('MODE_REPORT_ID')
            performance = mode_client.get_finance_forecast_performance(report_id)
            performance_cache[user_id] = performance
        except Exception as e:
            logger.error(f"Error fetching performance data: {e}")
            return

    # Build modal
    modal_view = {
        "type": "modal",
        "callback_id": "celebration_modal",
        "title": {
            "type": "plain_text",
            "text": "Post Celebration"
        },
        "submit": {
            "type": "plain_text",
            "text": "Post to Channel"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Performance Summary*\n\n"
                           f"• MTD Actual: *${performance['mtd_actual']:,.0f}K*\n"
                           f"• Finance Forecast: ${performance['finance_forecast']:,.0f}K\n"
                           f"• Beat by: *{performance['mtd_pct_vs_forecast']:.2f}%* "
                           f"(${performance['mtd_dollar_vs_forecast']:+,.0f}K)"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Step 1: Find a GIF*\n"
                           "Use Slack's `/giphy` command to search for a celebration GIF.\n"
                           "Copy the GIF URL and paste it below."
                }
            },
            {
                "type": "input",
                "block_id": "gif_url_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "gif_url_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://media.giphy.com/media/xyz/giphy.gif"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "GIF URL (Optional)"
                },
                "optional": True
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Step 2: Add a message (optional)*\n"
                           "Customize the celebration message or leave blank for default."
                }
            },
            {
                "type": "input",
                "block_id": "message_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "message_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "We crushed it! Great work team!"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Custom Message (Optional)"
                },
                "optional": True
            }
        ],
        "private_metadata": json.dumps({
            "channel_id": body['channel']['id'],
            "performance": performance
        })
    }

    try:
        client.views_open(trigger_id=trigger_id, view=modal_view)
    except SlackApiError as e:
        logger.error(f"Error opening modal: {e}")


@app.view("celebration_modal")
def handle_celebration_submission(ack, body, client, view):
    """
    Handle celebration modal submission.

    Posts the celebration message to the channel.
    """
    ack()

    user_id = body['user']['id']
    logger.info(f"Celebration submission by user {user_id}")

    # Extract metadata
    metadata = json.loads(view['private_metadata'])
    channel_id = metadata['channel_id']
    performance = metadata['performance']

    # Extract user inputs
    values = view['state']['values']
    gif_url = values['gif_url_block']['gif_url_input'].get('value', '').strip()
    custom_message = values['message_block']['message_input'].get('value', '').strip()

    # Build celebration message
    if custom_message:
        message_text = custom_message
    else:
        message_text = (
            f":tada: *We beat our forecast!* :tada:\n\n"
            f"*MTD Actual:* ${performance['mtd_actual']:,.0f}K\n"
            f"*Finance Forecast:* ${performance['finance_forecast']:,.0f}K\n"
            f"*Beat by:* {performance['mtd_pct_vs_forecast']:.2f}% "
            f"(${performance['mtd_dollar_vs_forecast']:+,.0f}K)"
        )

    # Build blocks
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text
            }
        }
    ]

    # Add GIF if provided
    if gif_url:
        # Validate URL
        if gif_url.startswith('http') and ('.gif' in gif_url or 'giphy.com' in gif_url or 'tenor.com' in gif_url):
            blocks.append({
                "type": "image",
                "image_url": gif_url,
                "alt_text": "Celebration!"
            })
        else:
            logger.warning(f"Invalid GIF URL provided: {gif_url}")

    try:
        # Post to channel
        client.chat_postMessage(
            channel=channel_id,
            text=message_text,
            blocks=blocks
        )

        logger.info(f"Celebration posted to channel {channel_id}")

        # Send confirmation DM
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=":white_check_mark: Celebration posted!"
        )

    except SlackApiError as e:
        logger.error(f"Error posting celebration: {e}")
        # Try to notify user
        try:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f":x: Error posting celebration: {e.response['error']}"
            )
        except:
            pass


@app.event("app_mention")
def handle_mention(event, client, say):
    """Handle @mentions of the bot."""
    text = event['text'].lower()

    if 'help' in text:
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Performance Celebration Bot* :chart_with_upwards_trend:\n\n"
                               "*Commands:*\n"
                               "• `/check-performance` - Check MTD performance vs forecast\n\n"
                               "*How it works:*\n"
                               "1. Run `/check-performance` to see current performance\n"
                               "2. If you're beating forecast, click the celebration button\n"
                               "3. Optionally add a GIF using `/giphy` and paste the URL\n"
                               "4. Post to the channel!"
                    }
                }
            ]
        )
    else:
        say("Hi! Use `/check-performance` to check performance, or mention me with `help` for more info.")


def main():
    """Start the bot."""
    logger.info("Starting Performance Celebration Bot...")

    # Check required environment variables
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_APP_TOKEN',
        'MODE_API_TOKEN',
        'MODE_API_SECRET',
        'MODE_WORKSPACE',
        'MODE_REPORT_ID'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    # Start the bot using Socket Mode
    try:
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        logger.info("Bot started successfully! Listening for events...")
        handler.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
