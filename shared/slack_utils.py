"""
Shared Slack utilities for all agents.

Provides common Slack functionality that can be reused across multiple agents.
"""

import os
from typing import Dict, List, Optional, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)


def get_slack_client(token: Optional[str] = None) -> WebClient:
    """
    Get a configured Slack WebClient.

    Args:
        token: Slack bot token (defaults to SLACK_BOT_TOKEN env var)

    Returns:
        Configured WebClient instance
    """
    bot_token = token or os.getenv('SLACK_BOT_TOKEN')
    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN must be set")

    return WebClient(token=bot_token)


def post_message(client: WebClient, channel: str, text: str,
                blocks: Optional[List[Dict]] = None,
                thread_ts: Optional[str] = None) -> Dict[str, Any]:
    """
    Post a message to Slack.

    Args:
        client: Slack WebClient instance
        channel: Channel ID or name
        text: Message text (fallback for notifications)
        blocks: Optional Slack Block Kit blocks
        thread_ts: Optional thread timestamp to reply in thread

    Returns:
        Slack API response

    Raises:
        SlackApiError: If posting fails
    """
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            thread_ts=thread_ts
        )
        logger.info(f"Message posted to {channel}")
        return response.data
    except SlackApiError as e:
        logger.error(f"Error posting message: {e.response['error']}")
        raise


def post_ephemeral(client: WebClient, channel: str, user: str, text: str,
                  blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Post an ephemeral message (only visible to specific user).

    Args:
        client: Slack WebClient instance
        channel: Channel ID
        user: User ID to show message to
        text: Message text
        blocks: Optional Slack Block Kit blocks

    Returns:
        Slack API response
    """
    try:
        response = client.chat_postEphemeral(
            channel=channel,
            user=user,
            text=text,
            blocks=blocks
        )
        logger.info(f"Ephemeral message posted to {user} in {channel}")
        return response.data
    except SlackApiError as e:
        logger.error(f"Error posting ephemeral message: {e.response['error']}")
        raise


def create_section_block(text: str, fields: Optional[List[str]] = None) -> Dict:
    """
    Create a Slack section block.

    Args:
        text: Main text (markdown supported)
        fields: Optional list of field texts

    Returns:
        Slack section block dict
    """
    block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }

    if fields:
        block["fields"] = [
            {"type": "mrkdwn", "text": field}
            for field in fields
        ]

    return block


def create_divider_block() -> Dict:
    """Create a Slack divider block."""
    return {"type": "divider"}


def create_header_block(text: str) -> Dict:
    """
    Create a Slack header block.

    Args:
        text: Header text (plain text only)

    Returns:
        Slack header block dict
    """
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": text
        }
    }


def create_image_block(image_url: str, alt_text: str = "Image",
                      title: Optional[str] = None) -> Dict:
    """
    Create a Slack image block.

    Args:
        image_url: URL of the image
        alt_text: Alt text for accessibility
        title: Optional title text

    Returns:
        Slack image block dict
    """
    block = {
        "type": "image",
        "image_url": image_url,
        "alt_text": alt_text
    }

    if title:
        block["title"] = {
            "type": "plain_text",
            "text": title
        }

    return block


def create_button(text: str, action_id: str, value: Optional[str] = None,
                 style: Optional[str] = None, url: Optional[str] = None) -> Dict:
    """
    Create a Slack button element.

    Args:
        text: Button text
        action_id: Unique action identifier
        value: Optional value to pass when clicked
        style: Optional style ("primary", "danger")
        url: Optional URL to open (instead of action)

    Returns:
        Slack button element dict
    """
    button = {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": text
        },
        "action_id": action_id
    }

    if value:
        button["value"] = value

    if style:
        button["style"] = style

    if url:
        button["url"] = url

    return button


def create_actions_block(elements: List[Dict]) -> Dict:
    """
    Create a Slack actions block.

    Args:
        elements: List of action elements (buttons, selects, etc.)

    Returns:
        Slack actions block dict
    """
    return {
        "type": "actions",
        "elements": elements
    }


def create_context_block(elements: List[str]) -> Dict:
    """
    Create a Slack context block.

    Args:
        elements: List of context text strings

    Returns:
        Slack context block dict
    """
    return {
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": elem}
            for elem in elements
        ]
    }


def format_user_mention(user_id: str) -> str:
    """Format a user mention."""
    return f"<@{user_id}>"


def format_channel_mention(channel_id: str) -> str:
    """Format a channel mention."""
    return f"<#{channel_id}>"


def format_link(url: str, text: str) -> str:
    """Format a hyperlink."""
    return f"<{url}|{text}>"


def test_connection(client: WebClient) -> bool:
    """
    Test the Slack connection.

    Args:
        client: Slack WebClient instance

    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = client.auth_test()
        logger.info(f"Connected to Slack workspace: {response['team']}")
        logger.info(f"Bot user: {response['user']}")
        return True
    except SlackApiError as e:
        logger.error(f"Connection test failed: {e.response['error']}")
        return False
