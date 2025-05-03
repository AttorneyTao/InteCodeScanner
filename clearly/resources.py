# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

# clearly/resources.py
"""
High‑level, read‑only helpers built on top of ClearlyDefinedClient.

New feature: each helper has `as_json=False` parameter –
set it to True to receive the raw JSON string from the API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .client import ClearlyDefinedClient
from .coordinates import Coordinate

_default_client = ClearlyDefinedClient()

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def get_definition(
    coord: str | Coordinate,
    *,
    client: ClearlyDefinedClient = _default_client,
    as_json: bool = False,  # NEW
) -> Dict[str, Any] | str:
    """Return the definition for a single component."""
    if isinstance(coord, str):
        coord = Coordinate.parse(coord)
    path = f"/definitions/{coord.to_path()}"
    return client.request("GET", path, raw=as_json)


def search(
    pattern: str,
    *,
    limit: int | None = None,
    client: ClearlyDefinedClient = _default_client,
    as_json: bool = False,  # NEW
) -> List[Dict[str, Any]] | str:
    """Fuzzy search coordinates that match `pattern`."""
    data = client.request(
        "GET", "/definitions", params={"pattern": pattern}, raw=as_json
    )
    if as_json:
        return data  # raw string
    return data[:limit] if limit else data


def get_definitions_bulk(
    coords: Sequence[str | Coordinate],
    *,
    client: ClearlyDefinedClient = _default_client,
    as_json: bool = False,  # NEW
) -> List[Dict[str, Any]] | str:
    """
    Batch‑fetch many definitions with POST /definitions.

    Returns list[dict] or raw JSON string depending on *as_json*.
    """
    coord_paths = [
        (Coordinate.parse(c) if isinstance(c, str) else c).to_path() for c in coords
    ]
    payload = {"coordinates": coord_paths}
    return client.request("POST", "/definitions", json=payload, raw=as_json)
