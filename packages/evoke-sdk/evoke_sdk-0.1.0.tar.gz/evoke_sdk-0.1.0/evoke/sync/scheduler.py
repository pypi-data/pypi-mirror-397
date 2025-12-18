"""
Evoke Sync - Background polling scheduler
"""
from typing import Optional, Callable
from threading import Thread, Event
import logging

logger = logging.getLogger(__name__)


class PollScheduler:
    """Background polling scheduler."""

    def __init__(self, interval_seconds: int = 300):
        self.interval = interval_seconds
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._callback: Optional[Callable] = None

    def start(self, callback: Callable) -> None:
        """Start background polling."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._callback = callback
        self._stop_event.clear()
        self._thread = Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.debug(f"Started signature polling (interval={self.interval}s)")

    def stop(self) -> None:
        """Stop background polling."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        logger.debug("Stopped signature polling")

    def _poll_loop(self) -> None:
        """Background polling loop."""
        while not self._stop_event.is_set():
            # Wait for interval or stop signal
            if self._stop_event.wait(timeout=self.interval):
                break

            if self._callback:
                try:
                    self._callback()
                except Exception as e:
                    logger.debug(f"Polling callback failed: {e}")

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._thread is not None and self._thread.is_alive()
