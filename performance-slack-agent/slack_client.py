"""
Slack Client
Handles posting messages and GIFs to Slack channels.
"""

import os
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)


class SlackClient:
    """Client for posting messages to Slack."""

    def __init__(self, bot_token: Optional[str] = None, channel_id: Optional[str] = None):
        """
        Initialize Slack client.

        Args:
            bot_token: Slack bot token (defaults to SLACK_BOT_TOKEN env var)
            channel_id: Default Slack channel ID (defaults to SLACK_CHANNEL_ID env var)
        """
        self.bot_token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        self.default_channel_id = channel_id or os.getenv('SLACK_CHANNEL_ID')

        if not self.bot_token:
            raise ValueError("SLACK_BOT_TOKEN must be set")

        self.client = WebClient(token=self.bot_token)
        logger.info("Slack client initialized")

    def post_message(self, text: str, channel_id: Optional[str] = None,
                    blocks: Optional[list] = None) -> Dict[str, Any]:
        """
        Post a text message to Slack.

        Args:
            text: Message text
            channel_id: Channel ID (uses default if not provided)
            blocks: Optional Slack block kit blocks

        Returns:
            Slack API response
        """
        channel = channel_id or self.default_channel_id
        if not channel:
            raise ValueError("Channel ID must be provided or set as default")

        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            logger.info(f"Message posted to channel {channel}")
            return response.data

        except SlackApiError as e:
            logger.error(f"Error posting message to Slack: {e.response['error']}")
            raise

    def post_celebration_message(self, gif_url: str, actual: float, forecast: float,
                                beat_percentage: float,
                                channel_id: Optional[str] = None,
                                custom_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a celebration message with GIF.

        Args:
            gif_url: URL of the celebration GIF
            actual: Actual performance value
            forecast: Forecast value
            beat_percentage: Percentage by which forecast was beaten
            channel_id: Channel ID (uses default if not provided)
            custom_message: Optional custom message text

        Returns:
            Slack API response
        """
        channel = channel_id or self.default_channel_id

        # Create a formatted message
        if custom_message:
            message = custom_message
        else:
            message = (
                f":tada: *We beat our forecast!* :tada:\n\n"
                f"*Actual:* {actual:,.2f}\n"
                f"*Forecast:* {forecast:,.2f}\n"
                f"*Beat by:* {beat_percentage:.1f}%"
            )

        # Create Slack blocks for a rich message
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "image",
                "image_url": gif_url,
                "alt_text": "Celebration!"
            }
        ]

        return self.post_message(text=message, channel_id=channel, blocks=blocks)

    def test_connection(self) -> bool:
        """
        Test the Slack connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to Slack workspace: {response['team']}")
            logger.info(f"Bot user: {response['user']}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack connection test failed: {e.response['error']}")
            return False

    def get_channel_info(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a Slack channel.

        Args:
            channel_id: Channel ID (uses default if not provided)

        Returns:
            Channel information
        """
        channel = channel_id or self.default_channel_id
        if not channel:
            raise ValueError("Channel ID must be provided or set as default")

        try:
            response = self.client.conversations_info(channel=channel)
            return response.data['channel']
        except SlackApiError as e:
            logger.error(f"Error getting channel info: {e.response['error']}")
            raise
