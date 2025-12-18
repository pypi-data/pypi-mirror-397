"""
Evoke Sync - Policy synchronization manager (internal use only)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from threading import Lock
import logging

from evoke.sync.policy_fetcher import PolicyFetcher
from evoke.sync.policy_cache import PolicyCache
from evoke.sync.policy_evaluator import PolicyEvaluator
from evoke.sync.scheduler import PollScheduler
from evoke.schema.policy import PolicyMatch

logger = logging.getLogger(__name__)


class PolicyManager:
    """
    Manages policy synchronization from platform (internal use only).

    Fetches policies from the backend and evaluates content against them.
    Not exposed to SDK consumers.

    Supports three sync modes:
    1. On init - sync_on_init()
    2. Background polling - start_polling()
    3. On-demand - sync_before_operation()
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        cache_dir: Optional[str] = None,
        poll_interval: int = 300,
    ):
        self.fetcher = PolicyFetcher(endpoint, api_key)
        self.cache = PolicyCache(cache_dir)
        self.evaluator = PolicyEvaluator()
        self.scheduler = PollScheduler(poll_interval)

        self._policies: List[dict] = []
        self._last_sync: Optional[datetime] = None
        self._sync_lock = Lock()

        # Load from cache on init
        cached_policies = self.cache.get_all()
        if cached_policies:
            self._policies = cached_policies
            logger.debug(f"Loaded {len(cached_policies)} policies from cache")

    def sync_on_init(self) -> bool:
        """
        Sync policies during SDK initialization.

        - Non-blocking: uses cached policies if available
        - Triggers background fetch if cache is stale
        """
        if self.cache.is_valid():
            # Use cache, trigger background refresh
            self._trigger_background_sync()
            return True

        # No valid cache, do synchronous fetch
        return self.sync_now(timeout=5.0)

    def start_polling(self) -> None:
        """Start background polling for policy updates."""
        self.scheduler.start(callback=self._on_poll)

    def stop_polling(self) -> None:
        """Stop background polling."""
        self.scheduler.stop()

    def sync_before_operation(self, max_age_seconds: int = 60) -> None:
        """
        Sync policies before an operation if stale.

        Only syncs if:
        - Cache is older than max_age_seconds
        - Not currently syncing
        """
        if self._should_sync(max_age_seconds):
            self.sync_now(timeout=2.0)

    def sync_now(self, timeout: float = 10.0) -> bool:
        """Synchronous policy fetch."""
        with self._sync_lock:
            try:
                data = self.fetcher.fetch(timeout=timeout)
                policies = data.get("policies", [])

                self.cache.update(policies)
                self._policies = policies
                self._last_sync = datetime.utcnow()

                logger.debug(f"Synced {len(policies)} policies")
                return True

            except Exception as e:
                logger.debug(f"Policy sync failed: {e}")
                return False

    def evaluate(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[PolicyMatch]:
        """
        Evaluate content against all policies.

        Args:
            content: The content to evaluate (e.g., user input, LLM output)
            context: Optional context dict with additional fields to check

        Returns:
            List of PolicyMatch objects for policies that matched
        """
        return self.evaluator.evaluate(content, self._policies, context)

    def get_policies(self) -> List[dict]:
        """Get all cached policies."""
        return self._policies.copy()

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

    @property
    def last_sync(self) -> Optional[datetime]:
        """Get last sync time."""
        return self._last_sync

    @property
    def policy_count(self) -> int:
        """Get number of cached policies."""
        return len(self._policies)
