"""
Evoke Sync - HTTP fetcher for SDK policies
"""
from typing import Dict, Any
import logging

from evoke._version import SDK_VERSION

logger = logging.getLogger(__name__)


class PolicyFetcher:
    """Fetches SDK policies from the Evoke platform."""

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key

    def fetch(self, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Fetch SDK policies from platform.

        Returns:
            Dict with 'policies', 'total'

        Raises:
            Exception on network/API error
        """
        try:
            import requests
        except ImportError:
            logger.warning("requests library not installed - cannot fetch policies")
            return {"policies": [], "total": 0}

        url = f"{self.endpoint}/sdk/policies"

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
                "policies": data.get("policies", []),
                "total": data.get("total", 0),
            }

        except Exception as e:
            logger.debug(f"Failed to fetch policies: {e}")
            raise
