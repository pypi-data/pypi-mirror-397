"""
Evoke Sync - Local policy cache
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from threading import Lock
import json
import os
import logging

logger = logging.getLogger(__name__)


class PolicyCache:
    """Local cache for SDK policies."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or self._default_cache_dir()
        self.cache_file = os.path.join(self.cache_dir, "policies.json")
        self._policies: List[dict] = []
        self._last_updated: Optional[datetime] = None
        self._version: Optional[str] = None
        self._lock = Lock()

        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Load from disk on init
        self._load_from_disk()

    def _default_cache_dir(self) -> str:
        """Get default cache directory."""
        home = os.path.expanduser("~")
        return os.path.join(home, ".evoke")

    def _load_from_disk(self) -> None:
        """Load policies from disk cache."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._policies = data.get("policies", [])
                    self._version = data.get("version")
                    updated_str = data.get("updated_at")
                    if updated_str:
                        self._last_updated = datetime.fromisoformat(updated_str)
                    logger.debug(f"Loaded {len(self._policies)} policies from cache")
        except Exception as e:
            logger.debug(f"Could not load policy cache: {e}")

    def _save_to_disk(self) -> None:
        """Save policies to disk cache."""
        try:
            data = {
                "policies": self._policies,
                "version": self._version,
                "updated_at": self._last_updated.isoformat() if self._last_updated else None,
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self._policies)} policies to cache")
        except Exception as e:
            logger.warning(f"Could not save policy cache: {e}")

    def is_valid(self, max_age_seconds: int = 3600) -> bool:
        """Check if cache is valid (not expired)."""
        if self._last_updated is None:
            return False
        age = (datetime.utcnow() - self._last_updated).total_seconds()
        return age < max_age_seconds

    def update(self, policies: List[dict], version: Optional[str] = None) -> None:
        """Update cache with new policies."""
        with self._lock:
            self._policies = policies
            self._version = version
            self._last_updated = datetime.utcnow()
            self._save_to_disk()

    def get_all(self) -> List[dict]:
        """Get all cached policies."""
        with self._lock:
            return self._policies.copy()

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self._policies = []
            self._version = None
            self._last_updated = None
            if os.path.exists(self.cache_file):
                try:
                    os.remove(self.cache_file)
                except Exception as e:
                    logger.debug(f"Could not remove cache file: {e}")

    @property
    def version(self) -> Optional[str]:
        """Get cached policy version."""
        return self._version

    @property
    def last_updated(self) -> Optional[datetime]:
        """Get last update time."""
        return self._last_updated

    @property
    def count(self) -> int:
        """Get number of cached policies."""
        return len(self._policies)
