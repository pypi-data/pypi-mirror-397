"""
Evoke Sync - HTTP fetcher for signatures
"""
from typing import List, Optional, Dict, Any
import logging

from evoke._version import SDK_VERSION

logger = logging.getLogger(__name__)


class SignatureFetcher:
    """Fetches signatures from the Evoke platform."""

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key

    def fetch(self, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Fetch signatures from platform.

        Returns:
            Dict with 'signatures', 'version', 'updated_at'

        Raises:
            Exception on network/API error
        """
        try:
            import requests
        except ImportError:
            logger.warning("requests library not installed - cannot fetch signatures")
            return {"signatures": [], "version": None, "updated_at": None}

        url = f"{self.endpoint}/signatures"

        try:
            response = requests.get(
                url,
                headers={
                    "X-API-Key": self.api_key,
                    "X-Evoke-Version": SDK_VERSION,
                },
                timeout=timeout,
            )
            response.raise_for_status()

            data = response.json()
            return {
                "signatures": data.get("signatures", []),
                "version": data.get("version"),
                "updated_at": data.get("updated_at"),
            }

        except Exception as e:
            logger.debug(f"Failed to fetch signatures: {e}")
            raise
