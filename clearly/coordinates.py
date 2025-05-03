# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

# clearly/coordinates.py
"""
Utility for parsing, validating, and serialising ClearlyDefined coordinates.

Coordinate grammar (production API):
    type/provider/namespace/name/revision
  or
    type/provider/namespace/name/revision/pr/<number>

`namespace` must ALWAYS be present; use "-" (hyphen) when none exists.

Key helpers
-----------
Coordinate.parse(raw_string)        -> Coordinate
Coordinate.from_parts(...)          -> Coordinate
coordinate.to_path()                -> "npm/npmjs/-/lodash/4.17.21"
coordinate.encoded()                -> "npm%2Fnpmjs%2F-%2Flodash%2F4.17.21"
coordinate.with_pr(123)             -> new Coordinate (immutable)
"""

from __future__ import annotations

from dataclasses import dataclass
import urllib.parse
from typing import Any


class CoordinateError(ValueError):
    """Raised when a coordinate string is syntactically invalid."""


@dataclass(frozen=True, slots=True)
class Coordinate:
    type: str
    provider: str
    namespace: str
    name: str
    revision: str
    pr: int | None = None

    # --------------------------------------------------------------------- #
    # Constructors
    # --------------------------------------------------------------------- #
    @classmethod
    def parse(cls, raw: str) -> "Coordinate":
        """
        Parse a raw coordinate string.

        Parameters
        ----------
        raw : str
            Coordinate text, e.g. "npm/npmjs/-/lodash/4.17.21"
            or with PR marker: "npm/npmjs/-/lodash/4.17.21/pr/42"

        Returns
        -------
        Coordinate
            Parsed, validated immutable object.

        Raises
        ------
        CoordinateError
            If the input does not conform to ClearlyDefined syntax.
        """
        if not raw or "/" not in raw:
            raise CoordinateError("Input is empty or missing '/' separators")

        parts = raw.split("/")
        if len(parts) == 7 and parts[5] == "pr":  # has PR
            base_parts, pr_part = parts[:5], parts[6]
            if not pr_part.isdigit():
                raise CoordinateError("PR segment must be 'pr/<int>'")
            pr = int(pr_part)
        elif len(parts) == 5:
            base_parts, pr = parts, None
        else:
            raise CoordinateError(
                "Coordinate must have 5 segments (or 7 including 'pr/<num>')"
            )

        type_, provider, namespace, name, revision = base_parts
        return cls(type_, provider, namespace, name, revision, pr)

    @classmethod
    def from_parts(
        cls,
        type: str,
        provider: str,
        namespace: str,
        name: str,
        revision: str,
        pr: str | int | None = None,
    ) -> "Coordinate":
        """
        Build a coordinate from individual columns (e.g. read from CSV).

        `pr` may be an int, a numeric‑looking string, or empty/None.
        """
        pr_int: int | None
        if pr in (None, "", "nan"):  # pandas sometimes reads empty as "nan"
            pr_int = None
        else:
            pr_int = int(pr)
        return cls(type, provider, namespace, name, revision, pr_int)

    # --------------------------------------------------------------------- #
    # Serialisation helpers
    # --------------------------------------------------------------------- #
    def to_path(self) -> str:
        """Raw path form used in REST URLs (no extra encoding)."""
        base = f"{self.type}/{self.provider}/{self.namespace}/{self.name}/{self.revision}"
        return f"{base}/pr/{self.pr}" if self.pr is not None else base

    def encoded(self) -> str:
        """
        Fully URL‑encode the coordinate (useful for query parameters).

        Example
        -------
        >>> Coordinate.parse("npm/npmjs/-/lodash/4.17.21").encoded()
        'npm%2Fnpmjs%2F-%2Flodash%2F4.17.21'
        """
        return urllib.parse.quote(self.to_path(), safe="")

    # --------------------------------------------------------------------- #
    # Convenience
    # --------------------------------------------------------------------- #
    def with_pr(self, pr_number: int) -> "Coordinate":
        """Return a copy with `pr` set to `pr_number` (immutable pattern)."""
        return Coordinate(
            self.type,
            self.provider,
            self.namespace,
            self.name,
            self.revision,
            pr_number,
        )

    def __str__(self) -> str:  # noqa: DunderStr
        return self.to_path()

    # Adding explicit __repr__ helps debugging
    def __repr__(self) -> str:  # noqa: D401, DunderRepr
        return f"Coordinate({self.to_path()})"
