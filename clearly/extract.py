# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

#extract.py
"""
Field‑selector helpers for ClearlyDefined definition JSON.

Problem
-------
Definitions are *deeply* nested.  Often you only care about a few
fields (declared license, parties, score …).

Solution
--------
`select_fields(definition, ["licensed.declared", "attribution.parties"])`
    → {"licensed.declared": "MIT", "attribution.parties": ["John Doe", ...]}

`select_fields_many(definitions, fields)` does the same for a list.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

__all__ = ["select_fields", "select_fields_many"]


def _get_path(d: Dict[str, Any], path: str) -> Any:
    """Follow a dotted path (no wildcards) inside nested dicts/lists."""
    cur: Any = d
    for segment in path.split("."):
        if isinstance(cur, list):
            # Allow numeric indexes if user wants "files.0.path"
            try:
                seg_int = int(segment)
            except ValueError:  # noqa: PERF203
                raise KeyError(f"Cannot index list with '{segment}'") from None
            try:
                cur = cur[seg_int]
            except IndexError as exc:
                raise KeyError(f"Index {seg_int} out of range") from exc
        else:  # dict‑like
            try:
                cur = cur[segment]
            except (TypeError, KeyError) as exc:
                raise KeyError(f"Missing key '{segment}' in '{path}'") from exc
    return cur


def select_fields(definition: Dict[str, Any], fields: Iterable[str]) -> Dict[str, Any]:
    """
    Extract just *fields* from one definition dict.

    Parameters
    ----------
    definition : dict
        Raw JSON from the API (`get_definition` result).
    fields : list[str]
        Dotted paths, e.g. "licensed.declared", "described.releaseDate".

    Returns
    -------
    dict
        Mapping field‑name → extracted value (missing keys omitted).
    """
    out: Dict[str, Any] = {}
    for f in fields:
        try:
            out[f] = _get_path(definition, f)
        except KeyError:
            # Skip silently – you may log if you prefer
            continue
    return out


def select_fields_many(
    definitions: List[Dict[str, Any]], fields: Iterable[str]
) -> List[Dict[str, Any]]:
    """Vectorised wrapper for a list of definitions."""
    return [select_fields(d, fields) for d in definitions]
