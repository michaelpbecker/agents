"""
Performance Slack Agent

Automated monitoring and celebration of performance metrics.
"""

from .agent import PerformanceSlackAgent
from .mode_client import ModeClient
from .slack_client import SlackClient
from .gif_selector import GifSelector

__version__ = "1.0.0"
__all__ = ['PerformanceSlackAgent', 'ModeClient', 'SlackClient', 'GifSelector']
