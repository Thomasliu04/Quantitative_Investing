from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from loguru import logger

T = TypeVar("T")


class RateLimiter:
    """Simple minimum-interval limiter between API calls."""

    def __init__(self, sleep_seconds: float = 0.15) -> None:
        self.sleep_seconds = sleep_seconds
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        gap = self.sleep_seconds - (now - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()


def with_retry(
    fn: Callable[[], T],
    *,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
    desc: str = "api_call",
) -> T:
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — API errors vary by provider
            last_exc = exc
            if attempt >= max_retries:
                break
            sleep_for = backoff_seconds * (2 ** (attempt - 1))
            logger.warning("{} failed ({}/{}): {}; retry in {:.1f}s", desc, attempt, max_retries, exc, sleep_for)
            time.sleep(sleep_for)
    assert last_exc is not None
    raise last_exc
