from __future__ import annotations

import logging
from typing import Callable, TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)
T = TypeVar("T")


def retry_with_backoff(*, attempts: int = 3, base: float = 1.0) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory that retries functions with exponential backoff.
    Intended for rate-limited HTTP APIs such as OpenAI and Notion.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return retry(
            wait=wait_exponential(multiplier=base, min=base, max=10),
            stop=stop_after_attempt(attempts),
            retry=retry_if_exception_type(Exception),
            reraise=True,
        )(func)

    return decorator
