from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterator


@dataclass
class ExponentialBackoff:
    timeout: timedelta = timedelta(minutes=10)
    initial_interval: timedelta = timedelta(milliseconds=250)
    max_interval: timedelta = timedelta(minutes=1)
    multiplier: float = 1.5
    random_factor: float = 0.5

    _start_time: datetime | None = field(default=None, init=False)
    _current: timedelta | None = field(default=None, init=False)

    def reset(self) -> None:
        """Reset the backoff state."""
        self._start_time = None
        self._current = None

    def _compute_next_delay(self) -> float:
        """Compute next delay (in seconds) using exponential backoff with jitter."""
        if self._current is None:
            next_delay = self.initial_interval
        else:
            next_delay = min(
                timedelta(seconds=self._current.total_seconds() * self.multiplier),
                self.max_interval,
            )

        # jitter
        jitter = next_delay.total_seconds() * self.random_factor
        randomized_delay = next_delay.total_seconds() + random.uniform(-jitter, jitter)
        randomized_delay = max(randomized_delay, 0.0)

        self._current = timedelta(seconds=randomized_delay)
        return randomized_delay

    def is_expired(self) -> bool:
        """Return True if total elapsed time exceeds the timeout."""
        if self._start_time is None:
            return False
        return datetime.now(timezone.utc) - self._start_time >= self.timeout

    def delays(self) -> Iterator[float]:
        """
        Yield delays (seconds). Stops when timeout expires.
        Does NOT sleep.
        """
        self.reset()
        self._start_time = datetime.now(timezone.utc)

        while not self.is_expired():
            yield self._compute_next_delay()

    def sleeps(self) -> Iterator[None]:
        """
        Sleep using exponential backoff. Yield after each sleep.
        Caller (e.g. Operation.wait) uses this to poll to perform work between sleeps.
        """
        for delay in self.delays():
            time.sleep(delay)
            yield
