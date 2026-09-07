"""HTTP retry with exponential backoff + full jitter.

Blog: https://automate-lab.tistory.com/20
"""
from __future__ import annotations

import json
import logging
import random
import time
import urllib.error
import urllib.request
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


class HttpRetryError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


def _sleep_seconds(
    attempt: int,
    *,
    base: float,
    max_backoff: float,
    retry_after: float | None,
) -> float:
    if retry_after is not None and retry_after > 0:
        return min(retry_after, max_backoff)
    exp = min(max_backoff, base * (2 ** (attempt - 1)))
    return random.uniform(0, exp)


def call_with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_backoff: float = 1.0,
    max_backoff: float = 30.0,
    retry_on: Callable[[BaseException], tuple[bool, float | None]] | None = None,
) -> T:
    """Retry an arbitrary callable. retry_on returns (should_retry, retry_after|None)."""
    last: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except BaseException as exc:
            last = exc
            should, retry_after = (True, None)
            if retry_on is not None:
                should, retry_after = retry_on(exc)
            if not should or attempt >= max_attempts:
                raise
            delay = _sleep_seconds(
                attempt,
                base=base_backoff,
                max_backoff=max_backoff,
                retry_after=retry_after,
            )
            logger.warning(
                "attempt %s/%s failed: %s; sleep %.2fs",
                attempt,
                max_attempts,
                exc,
                delay,
            )
            time.sleep(delay)
    assert last is not None
    raise last


def _retry_after_from_headers(headers: Any) -> float | None:
    try:
        raw = headers.get("Retry-After")
    except Exception:
        return None
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def urllib_request_with_retry(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    method: str = "GET",
    timeout: float = 15.0,
    max_attempts: int = 5,
) -> tuple[int, bytes]:
    """Return (status, body). Non-retryable errors raise HttpRetryError."""

    def once() -> tuple[int, bytes]:
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers or {},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in RETRY_STATUS:
                ra = _retry_after_from_headers(exc.headers)
                err = HttpRetryError(
                    f"HTTP {exc.code}",
                    status=exc.code,
                    body=body,
                )
                err.retry_after = ra  # type: ignore[attr-defined]
                raise err from exc
            raise HttpRetryError(
                f"HTTP {exc.code}: {body[:300]}",
                status=exc.code,
                body=body,
            ) from exc
        except urllib.error.URLError as exc:
            raise HttpRetryError(f"URLError: {exc}") from exc

    def decide(exc: BaseException) -> tuple[bool, float | None]:
        if isinstance(exc, HttpRetryError) and exc.status in RETRY_STATUS:
            return True, getattr(exc, "retry_after", None)
        if isinstance(exc, HttpRetryError) and exc.status is None:
            return True, None
        return False, None

    return call_with_retry(
        once,
        max_attempts=max_attempts,
        retry_on=decide,
    )


def post_json(url: str, payload: dict[str, Any], **kwargs: Any) -> tuple[int, bytes]:
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", **(kwargs.pop("headers", {}) or {})}
    return urllib_request_with_retry(
        url, data=data, headers=headers, method="POST", **kwargs
    )
