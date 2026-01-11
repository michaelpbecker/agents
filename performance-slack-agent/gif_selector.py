"""
GIF Selector
Handles selection of celebration GIFs using Giphy API.
"""

import os
import requests
import random
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GifSelector:
    """Selects celebration GIFs using Giphy API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GIF selector.

        Args:
            api_key: Giphy API key (defaults to GIPHY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GIPHY_API_KEY')

        if not self.api_key:
            logger.warning("No GIPHY_API_KEY provided, using fallback GIFs")

        self.base_url = "https://api.giphy.com/v1/gifs"

        # Fallback celebration GIF URLs if Giphy API is not available
        self.fallback_gifs = [
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",  # Confetti
            "https://media.giphy.com/media/g9582DNuQppxC/giphy.gif",  # Celebration
            "https://media.giphy.com/media/l0HlQGLVn0QohrKY8/giphy.gif",  # Fireworks
            "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif",  # Party
            "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif",  # Success
        ]

    def search_celebration_gif(self, query: str = "celebration success", limit: int = 25) -> List[Dict]:
        """
        Search for celebration GIFs.

        Args:
            query: Search query for GIFs
            limit: Number of results to fetch

        Returns:
            List of GIF dictionaries with 'url' and 'title' keys
        """
        if not self.api_key:
            logger.info("Using fallback GIFs")
            return [{'url': url, 'title': 'Celebration!'} for url in self.fallback_gifs]

        try:
            params = {
                'api_key': self.api_key,
                'q': query,
                'limit': limit,
                'rating': 'g',  # Keep it professional
                'lang': 'en'
            }

            response = requests.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()

            data = response.json()
            gifs = []

            for gif in data.get('data', []):
                gifs.append({
                    'url': gif['images']['original']['url'],
                    'title': gif.get('title', 'Celebration!'),
                    'gif_id': gif.get('id')
                })

            logger.info(f"Found {len(gifs)} celebration GIFs")
            return gifs

        except Exception as e:
            logger.error(f"Error fetching GIFs from Giphy: {e}")
            logger.info("Falling back to default GIFs")
            return [{'url': url, 'title': 'Celebration!'} for url in self.fallback_gifs]

    def get_random_celebration_gif(self, query: str = "celebration success") -> Dict:
        """
        Get a random celebration GIF.

        Args:
            query: Search query for GIFs

        Returns:
            Dictionary with 'url' and 'title' keys
        """
        gifs = self.search_celebration_gif(query)
        if not gifs:
            raise ValueError("No GIFs found")

        selected = random.choice(gifs)
        logger.info(f"Selected GIF: {selected['title']}")
        return selected

    def get_trending_celebration_gif(self) -> Dict:
        """
        Get a trending celebration GIF.

        Returns:
            Dictionary with 'url' and 'title' keys
        """
        if not self.api_key:
            logger.info("Using fallback GIF")
            return {'url': random.choice(self.fallback_gifs), 'title': 'Celebration!'}

        try:
            params = {
                'api_key': self.api_key,
                'limit': 25,
                'rating': 'g'
            }

            response = requests.get(f"{self.base_url}/trending", params=params)
            response.raise_for_status()

            data = response.json()

            # Filter for celebration-related GIFs
            celebration_keywords = ['celebration', 'party', 'success', 'winner', 'champion', 'congrats']
            celebration_gifs = []

            for gif in data.get('data', []):
                title = gif.get('title', '').lower()
                if any(keyword in title for keyword in celebration_keywords):
                    celebration_gifs.append({
                        'url': gif['images']['original']['url'],
                        'title': gif.get('title', 'Celebration!'),
                        'gif_id': gif.get('id')
                    })

            if celebration_gifs:
                selected = random.choice(celebration_gifs)
                logger.info(f"Selected trending GIF: {selected['title']}")
                return selected
            else:
                # Fall back to random search if no trending celebration GIFs
                return self.get_random_celebration_gif()

        except Exception as e:
            logger.error(f"Error fetching trending GIFs: {e}")
            return self.get_random_celebration_gif()
