"""
Evoke Core - Event buffering and HTTP delivery to backend
"""
from typing import List, Optional
from threading import Thread, Lock
import time
import logging
import atexit
import json

from evoke.schema import Event
from evoke._version import SDK_VERSION

logger = logging.getLogger(__name__)

# Global transport instance
_transport: Optional["EventTransport"] = None


def get_transport() -> Optional["EventTransport"]:
    """Get the global transport instance"""
    return _transport


def set_transport(transport: "EventTransport") -> None:
    """Set the global transport instance"""
    global _transport
    _transport = transport


class EventTransport:
    """
    Buffers events and sends them to the Evoke platform via /api/v1/events.

    Features:
    - Batches events for efficiency
    - Time-based flush for low-volume scenarios
    - Thread-safe buffering
    - Automatic flush on exit
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        buffer_size: int = 100,
        flush_interval: float = 5.0,
        timeout: float = 10.0,
        realtime: bool = True,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.timeout = timeout
        self.realtime = realtime

        self.buffer: List[Event] = []
        self._lock = Lock()
        self._flush_thread: Optional[Thread] = None
        self._running = False
        self._pending_threads: List[Thread] = []
        self._threads_lock = Lock()

        if not realtime:
            self._start_flush_thread()

        atexit.register(self._shutdown)

    def _start_flush_thread(self):
        """Start the background flush thread"""
        self._running = True
        self._flush_thread = Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

    def _flush_loop(self):
        """Background loop that periodically flushes the buffer"""
        while self._running:
            time.sleep(self.flush_interval)
            if self.buffer:
                self.flush()

    def _track_thread(self, thread: Thread) -> None:
        """Track a thread and clean up completed ones."""
        with self._threads_lock:
            # Clean up completed threads
            self._pending_threads = [t for t in self._pending_threads if t.is_alive()]
            self._pending_threads.append(thread)

    def send(self, event: Event) -> None:
        """
        Send an event to the backend.

        In realtime mode (default): Event is sent immediately in a background thread.
        In batched mode: Event is buffered and sent when buffer is full or flush is called.
        """
        if self.realtime:
            thread = Thread(target=self._send_events, args=([event],))
            thread.start()
            self._track_thread(thread)
        else:
            with self._lock:
                self.buffer.append(event)
                if len(self.buffer) >= self.buffer_size:
                    self._flush_internal()

    def flush(self) -> bool:
        """Force send all buffered events and wait for pending sends to complete."""
        # First flush any buffered events
        with self._lock:
            self._flush_internal()

        # Wait for all pending threads to complete
        with self._threads_lock:
            threads = self._pending_threads.copy()

        for thread in threads:
            thread.join(timeout=self.timeout)

        return True

    def _flush_internal(self) -> bool:
        """Internal flush - must be called with lock held."""
        if not self.buffer:
            return True

        events = self.buffer.copy()
        self.buffer.clear()

        Thread(target=self._send_events, args=(events,), daemon=True).start()
        return True

    def _send_events(self, events: List[Event]) -> bool:
        """Send events to the backend /api/v1/events endpoint."""
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed - cannot send events")
            return False

        url = f"{self.endpoint}/events"

        payload = {
            "events": [e.to_dict() for e in events]
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "X-Evoke-Version": SDK_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )

            if response.status_code in (200, 201):
                logger.debug(f"Sent {len(events)} events to {url}")
                return True
            else:
                logger.warning(f"Failed to send events: {response.status_code} {response.text}")
                with self._lock:
                    self.buffer.extend(events)
                return False

        except Exception as e:
            logger.warning(f"Error sending events: {e}")
            with self._lock:
                self.buffer.extend(events)
            return False

    def _shutdown(self):
        """Cleanup on application exit"""
        self._running = False

        # Wait for pending threads to complete
        with self._threads_lock:
            threads = self._pending_threads.copy()

        for thread in threads:
            thread.join(timeout=2.0)  # Short timeout on shutdown

        # Flush any remaining buffered events synchronously
        with self._lock:
            if self.buffer:
                events = self.buffer.copy()
                self.buffer.clear()
                self._send_events_sync(events)

    def _send_events_sync(self, events: List[Event]) -> bool:
        """Synchronous event send for shutdown."""
        try:
            import requests
        except ImportError:
            return False

        url = f"{self.endpoint}/events"

        payload = {
            "events": [e.to_dict() for e in events]
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "X-Evoke-Version": SDK_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            return response.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"Error in final flush: {e}")
            return False

    @property
    def pending_count(self) -> int:
        """Number of events waiting to be sent"""
        with self._lock:
            return len(self.buffer)


class FileTransport:
    """
    Transport that saves events to a local JSON file.
    Useful for debugging and testing without a backend.
    """

    def __init__(self, file_path: str = "./evoke_events.json"):
        self.file_path = file_path
        self._lock = Lock()
        self.events: List[Event] = []

        try:
            with open(self.file_path, 'r') as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    self.events = []
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.file_path, 'w') as f:
                json.dump([], f)

    def send(self, event: Event) -> None:
        """Save event to file immediately"""
        with self._lock:
            self.events.append(event)
            self._write_to_file()
        logger.debug(f"[EVOKE EVENT] {event.event_type} saved to {self.file_path}")

    def _write_to_file(self):
        """Write all events to file"""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(
                    [e.to_dict() for e in self.events],
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Failed to write events to file: {e}")

    def flush(self) -> bool:
        """Ensure all events are written to file"""
        with self._lock:
            self._write_to_file()
        return True

    def get_events(self) -> List[Event]:
        """Get all captured events"""
        with self._lock:
            return self.events.copy()

    def get_file_path(self) -> str:
        """Get the path to the events file"""
        return self.file_path


class DebugTransport:
    """
    Debug transport that prints events instead of sending them.
    Useful for development and testing.
    """

    def __init__(self, **kwargs):
        self.buffer: List[Event] = []
        self._lock = Lock()
        self.captured_events: List[Event] = []

    def send(self, event: Event) -> None:
        """Capture event for inspection"""
        with self._lock:
            self.captured_events.append(event)

        event_dict = event.to_dict()
        logger.info(f"[EVOKE EVENT] {event.event_type}: {json.dumps(event_dict, indent=2)}")

    def flush(self) -> bool:
        """No-op for debug transport"""
        return True

    def get_events(self) -> List[Event]:
        """Get all captured events"""
        with self._lock:
            return self.captured_events.copy()

    def clear(self):
        """Clear captured events"""
        with self._lock:
            self.captured_events.clear()
