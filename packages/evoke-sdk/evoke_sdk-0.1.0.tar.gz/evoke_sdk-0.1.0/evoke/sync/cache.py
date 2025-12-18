"""
Evoke Sync - Local signature cache
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from threading import Lock
import json
import os
import logging

logger = logging.getLogger(__name__)


class SignatureCache:
    """Local cache for signatures."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or self._default_cache_dir()
        self.cache_file = os.path.join(self.cache_dir, "signatures.json")
        self._signatures: List[dict] = []
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
        """Load signatures from disk cache."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._signatures = data.get("signatures", [])
                    self._version = data.get("version")
                    updated_str = data.get("updated_at")
                    if updated_str:
                        self._last_updated = datetime.fromisoformat(updated_str)
                    logger.debug(f"Loaded {len(self._signatures)} signatures from cache")
        except Exception as e:
            logger.debug(f"Could not load signature cache: {e}")

    def _save_to_disk(self) -> None:
        """Save signatures to disk cache."""
        try:
            data = {
                "signatures": self._signatures,
                "version": self._version,
                "updated_at": self._last_updated.isoformat() if self._last_updated else None,
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self._signatures)} signatures to cache")
        except Exception as e:
            logger.warning(f"Could not save signature cache: {e}")

    def is_valid(self, max_age_seconds: int = 3600) -> bool:
        """Check if cache is valid (not expired)."""
        if self._last_updated is None:
            return False
        age = (datetime.utcnow() - self._last_updated).total_seconds()
        return age < max_age_seconds

    def update(self, signatures: List[dict], version: Optional[str] = None) -> None:
        """Update cache with new signatures."""
        with self._lock:
            self._signatures = signatures
            self._version = version
            self._last_updated = datetime.utcnow()
            self._save_to_disk()

    def get_all(self) -> List[dict]:
        """Get all cached signatures."""
        with self._lock:
            return self._signatures.copy()

    @property
    def version(self) -> Optional[str]:
        """Get cached signature version."""
        return self._version

    @property
    def last_updated(self) -> Optional[datetime]:
        """Get last update time."""
        return self._last_updated

    @property
    def count(self) -> int:
        """Get number of cached signatures."""
        return len(self._signatures)
