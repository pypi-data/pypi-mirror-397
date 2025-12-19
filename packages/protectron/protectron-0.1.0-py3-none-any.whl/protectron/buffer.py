"""Thread-safe event buffer with disk persistence."""

import json
import logging
import threading
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, Dict, List, Optional

from protectron.events import Event
from protectron.exceptions import BufferFullError

logger = logging.getLogger("protectron.buffer")


class EventBuffer:
    """
    Thread-safe event buffer with optional disk persistence.

    When events can't be sent (network issues), they're buffered here
    and retried on the next flush.
    """

    def __init__(
        self,
        max_size: int = 1000,
        persist_path: Optional[str] = None,
        overflow_strategy: str = "drop_oldest",
    ):
        """
        Initialize the event buffer.

        Args:
            max_size: Maximum events to buffer
            persist_path: Optional path for disk persistence
            overflow_strategy: What to do when full - 'drop_oldest', 'drop_newest', or 'raise'
        """
        if overflow_strategy not in ("drop_oldest", "drop_newest", "raise"):
            raise ValueError(
                "overflow_strategy must be 'drop_oldest', 'drop_newest', or 'raise'"
            )

        self._max_size = max_size
        self._overflow_strategy = overflow_strategy
        self._persist_path = Path(persist_path) if persist_path else None
        self._buffer: Deque[Event] = deque()
        self._lock = threading.RLock()
        self._total_added = 0
        self._total_dropped = 0

        if self._persist_path and self._persist_path.exists():
            self._load_from_disk()

    def add(self, event: Event) -> bool:
        """
        Add an event to the buffer.

        Thread-safe. Returns True if event was added.

        Args:
            event: Event to add

        Returns:
            True if event was added, False if dropped

        Raises:
            BufferFullError: If overflow_strategy is 'raise' and buffer is full
        """
        with self._lock:
            if len(self._buffer) >= self._max_size:
                if self._overflow_strategy == "drop_oldest":
                    self._buffer.popleft()
                    self._total_dropped += 1
                    logger.warning("Buffer full, dropped oldest event")
                elif self._overflow_strategy == "drop_newest":
                    self._total_dropped += 1
                    logger.warning("Buffer full, dropping new event")
                    return False
                elif self._overflow_strategy == "raise":
                    raise BufferFullError(f"Buffer full ({self._max_size} events)")

            self._buffer.append(event)
            self._total_added += 1
            return True

    def add_many(self, events: List[Event]) -> int:
        """
        Add multiple events to the buffer.

        Args:
            events: List of events to add

        Returns:
            Number of events successfully added
        """
        return sum(1 for e in events if self.add(e))

    def get_batch(self, size: int) -> List[Event]:
        """
        Get a batch of events from the buffer.

        Events are removed from the buffer. If sending fails,
        use return_batch() to put them back.

        Args:
            size: Maximum number of events to return

        Returns:
            List of events (may be less than size)
        """
        with self._lock:
            batch: List[Event] = []
            for _ in range(min(size, len(self._buffer))):
                batch.append(self._buffer.popleft())
            return batch

    def return_batch(self, events: List[Event]) -> None:
        """
        Return a batch of events to the front of the buffer.

        Use this when sending fails to preserve event order.

        Args:
            events: Events to return to buffer
        """
        with self._lock:
            for event in reversed(events):
                self._buffer.appendleft(event)

    def peek(self, size: int) -> List[Event]:
        """
        Peek at events without removing them.

        Args:
            size: Maximum number of events to peek

        Returns:
            List of events
        """
        with self._lock:
            return list(self._buffer)[:size]

    def size(self) -> int:
        """Get current buffer size."""
        with self._lock:
            return len(self._buffer)

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        with self._lock:
            return len(self._buffer) == 0

    def is_full(self) -> bool:
        """Check if buffer is at capacity."""
        with self._lock:
            return len(self._buffer) >= self._max_size

    def clear(self) -> int:
        """
        Clear the buffer.

        Returns:
            Number of events cleared
        """
        with self._lock:
            count = len(self._buffer)
            self._buffer.clear()
            return count

    def stats(self) -> Dict[str, object]:
        """
        Get buffer statistics.

        Returns:
            Dictionary with buffer stats
        """
        with self._lock:
            current_size = len(self._buffer)
            return {
                "current_size": current_size,
                "max_size": self._max_size,
                "total_added": self._total_added,
                "total_dropped": self._total_dropped,
                "utilization": current_size / self._max_size if self._max_size > 0 else 0,
                "overflow_strategy": self._overflow_strategy,
            }

    def persist_to_disk(self) -> int:
        """
        Persist buffer contents to disk for crash recovery.

        Returns:
            Number of events persisted
        """
        if not self._persist_path:
            return 0

        with self._lock:
            if not self._buffer:
                if self._persist_path.exists():
                    self._persist_path.unlink()
                return 0

            events_data = [e.to_dict() for e in self._buffer]

        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self._persist_path.with_suffix(".tmp")

            with open(temp_path, "w") as f:
                json.dump(
                    {
                        "version": 1,
                        "persisted_at": datetime.now(timezone.utc).isoformat(),
                        "events": events_data,
                    },
                    f,
                )

            temp_path.replace(self._persist_path)
            logger.debug(f"Persisted {len(events_data)} events to disk")
            return len(events_data)

        except Exception as e:
            logger.error(f"Failed to persist events: {e}")
            return 0

    def _load_from_disk(self) -> int:
        """
        Load persisted events from disk.

        Returns:
            Number of events loaded
        """
        if not self._persist_path or not self._persist_path.exists():
            return 0

        try:
            with open(self._persist_path, "r") as f:
                data = json.load(f)

            loaded = 0
            for event_data in data.get("events", []):
                try:
                    event = Event.from_dict(event_data)
                    self._buffer.append(event)
                    loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to load event: {e}")

            self._persist_path.unlink()
            logger.info(f"Loaded {loaded} persisted events from disk")
            return loaded

        except Exception as e:
            logger.error(f"Failed to load persisted events: {e}")
            return 0

    def __len__(self) -> int:
        """Return buffer size."""
        return self.size()

    def __bool__(self) -> bool:
        """Return True if buffer has events."""
        return not self.is_empty()
