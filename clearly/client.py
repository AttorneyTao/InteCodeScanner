# clearly/client.py
"""
Low‑level HTTP wrapper for the ClearlyDefined REST API.

Adds optional *raw=True* flag so callers can get the exact JSON string
returned by the API instead of the usual parsed Python dict/list.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #
class ApiError(Exception):
    """Base class for ClearlyDefined client errors."""


class RateLimitExceeded(ApiError):
    """Raised when the max retry window for 429 responses is exceeded."""


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #
class ClearlyDefinedClient:
    """Synchronous client with automatic 429 retry + raw‑response option."""

    def __init__(
        self,
        base_url: str = "https://api.clearlydefined.io",
        *,
        timeout: float | int = 15,
        user_agent: str = "clearly-py/0.1",
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "application/json",
            }
        )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None,
        raw: bool = False,  # NEW
    ) -> Any | str:
        """
        Make an HTTP request, retrying on 429.

        Parameters
        ----------
        raw : bool, default False
            * False → return `response.json()`  (parsed Python object)
            * True  → return `response.text`    (raw JSON string)
        """
        url = f"{self.base_url}{path}"
        attempts = 0

        while True:
            resp = self.session.request(
                method,
                url,
                timeout=self.timeout,
                params=params,
                json=json,
                headers=headers,
            )

            # ------------------------ success ----------------------------- #
            if resp.status_code < 400:
                return resp.text if raw else resp.json()

            # ------------------- rate‑limited ----------------------------- #
            if resp.status_code == 429 and attempts < self.max_retries:
                attempts += 1
                self._handle_rate_limit(resp, attempts)
                continue

            # --------------------- other errors --------------------------- #
            if resp.status_code == 429:
                raise RateLimitExceeded("Exceeded retry budget for 429 response")
            raise ApiError(f"{resp.status_code} {resp.reason}: {resp.text[:240]}")

    # --------------------------------------------------------------------- #
    # Internals
    # --------------------------------------------------------------------- #
    def _handle_rate_limit(self, resp: requests.Response, attempt: int) -> None:
        """Sleep until reset (or exponential back‑off)."""
        reset_sec = self._parse_reset_header(resp.headers)
        if reset_sec is None:
            reset_sec = pow(self.backoff_factor, attempt)
            log.warning("429 → backing off %.1f s (exponential)", reset_sec)
        else:
            log.warning("429 → sleeping %.1f s until X‑RateLimit‑Reset", reset_sec)
        time.sleep(reset_sec)

    @staticmethod
    def _parse_reset_header(headers: Dict[str, str]) -> float | None:
        """Return seconds until reset or None if header missing/invalid."""
        reset_val = headers.get("x-ratelimit-reset")
        if not reset_val:
            return None
        try:
            reset_epoch = int(reset_val)
        except ValueError:
            return None
        return max(reset_epoch - time.time(), 0.0)

    # -- context manager --------------------------------------------------- #
    def __enter__(self):  # noqa: D401
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: D401
        self.session.close()
