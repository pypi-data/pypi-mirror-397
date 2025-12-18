"""
Evoke Sync - Signature synchronization manager
"""
from typing import Optional, List
from datetime import datetime
from threading import Lock
import logging

from evoke.sync.fetcher import SignatureFetcher
from evoke.sync.cache import SignatureCache
from evoke.sync.scheduler import PollScheduler

logger = logging.getLogger(__name__)


class SignatureManager:
    """
    Manages signature synchronization from platform.

    Supports three sync modes:
    1. On init - sync_on_init()
    2. Background polling - start_polling()
    3. On-demand - sync_before_analyze()
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        cache_dir: Optional[str] = None,
        poll_interval: int = 300,
    ):
        self.fetcher = SignatureFetcher(endpoint, api_key)
        self.cache = SignatureCache(cache_dir)
        self.scheduler = PollScheduler(poll_interval)

        self._last_sync: Optional[datetime] = None
        self._sync_lock = Lock()

    def sync_on_init(self) -> bool:
        """
        Sync signatures during SDK initialization.

        - Non-blocking: uses cached signatures if available
        - Triggers background fetch if cache is stale
        """
        if self.cache.is_valid():
            # Use cache, trigger background refresh
            self._trigger_background_sync()
            return True

        # No valid cache, do synchronous fetch
        return self.sync_now(timeout=5.0)

    def start_polling(self) -> None:
        """Start background polling for signature updates."""
        self.scheduler.start(callback=self._on_poll)

    def stop_polling(self) -> None:
        """Stop background polling."""
        self.scheduler.stop()

    def sync_before_analyze(self, max_age_seconds: int = 60) -> None:
        """
        Sync signatures before analyze() call if stale.

        Only syncs if:
        - Cache is older than max_age_seconds
        - Not currently syncing
        """
        if self._should_sync(max_age_seconds):
            self.sync_now(timeout=2.0)

    def sync_now(self, timeout: float = 10.0) -> bool:
        """Synchronous signature fetch."""
        with self._sync_lock:
            try:
                data = self.fetcher.fetch(timeout=timeout)
                signatures = data.get("signatures", [])
                version = data.get("version")

                self.cache.update(signatures, version)
                self._last_sync = datetime.utcnow()

                # Apply signatures to detection engine
                self._apply_signatures(signatures)

                logger.debug(f"Synced {len(signatures)} signatures (v{version})")
                return True

            except Exception as e:
                logger.debug(f"Signature sync failed: {e}")
                return False

    def get_signatures(self) -> List[dict]:
        """Get current signatures (from cache)."""
        return self.cache.get_all()

    def _should_sync(self, max_age_seconds: int) -> bool:
        """Check if we should sync based on cache age."""
        if not self.cache.is_valid(max_age_seconds):
            return True
        return False

    def _trigger_background_sync(self) -> None:
        """Trigger a background sync."""
        from threading import Thread
        Thread(target=self.sync_now, daemon=True).start()

    def _on_poll(self) -> None:
        """Callback for scheduler polling."""
        self.sync_now(timeout=10.0)

    def _apply_signatures(self, signatures: List[dict]) -> None:
        """Apply signatures to the detection engine."""
        try:
            from evoke.detection import get_registry
            from evoke.detection.rules.base import RegexRule

            registry = get_registry()

            for sig in signatures:
                if sig.get("type") == "regex":
                    rule = RegexRule(
                        rule_id=sig.get("id", "unknown"),
                        name=sig.get("name", "Unknown"),
                        pattern=sig.get("pattern", ""),
                        category=sig.get("category", "custom"),
                        severity=sig.get("severity", "medium"),
                        confidence=sig.get("confidence", 0.8),
                    )
                    registry.add_rule(rule)

            logger.debug(f"Applied {len(signatures)} signatures to detection engine")

        except Exception as e:
            logger.debug(f"Could not apply signatures: {e}")


# Global signature manager instance
_manager: Optional[SignatureManager] = None


def get_signature_manager() -> Optional[SignatureManager]:
    """Get the global signature manager."""
    return _manager


def set_signature_manager(manager: SignatureManager) -> None:
    """Set the global signature manager."""
    global _manager
    _manager = manager
