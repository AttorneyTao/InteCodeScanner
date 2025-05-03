# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

"""
server/services/enrich.py  (v4)

Enrichment logic that keeps:
* compiled_coord          → definition result
* namespace search coord  → definition result
* name search coord       → definition result

Adds 10 columns total (1+3) x 3 groups.
"""

from __future__ import annotations

import pandas as pd
from typing import Any, Dict

from clearly.resources import search as cd_search, get_definition
from clearly.coordinates import Coordinate, CoordinateError

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _compile_coord(row: pd.Series) -> str:
    """Build coordinate string from CSV fields even if revision is missing."""
    _type = str(row.get("type", "")).strip()
    provider = str(row.get("provider", "")).strip()
    namespace = str(row.get("namespace", "")).strip() or "-"
    name = str(row.get("name", "")).strip()
    revision = str(row.get("revision", "")).strip()

    parts = [_type, provider, namespace, name]
    if revision:
        parts.append(revision)
    return "/".join(parts)


def _extract(defn: Dict[str, Any]) -> Dict[str, str]:
    licensed = defn.get("licensed", {})
    declared = str(licensed.get("declared", ""))
    tool_total = str(licensed.get("toolScore", {}).get("total", ""))

    parties = (
        licensed.get("facets", {})
        .get("core", {})
        .get("attribution", {})
        .get("parties", [])
    )
    parties_concat = "; ".join(parties) if parties else ""
    return dict(declared=declared, toolScore_total=tool_total, parties=parties_concat)


def _enrich_coord(coord: str) -> Dict[str, str]:
    """Fetch definition for *coord* → trio dict; blank dict on failure."""
    if not coord:
        return dict(declared="", toolScore_total="", parties="")
    try:
        defn = get_definition(coord)
        return _extract(defn)
    except Exception:  # noqa: BLE001
        return dict(declared="", toolScore_total="", parties="")


def _first_coord_from_search(pattern: str) -> str:
    """Return first coordinate string for search pattern, or ''."""
    hits = cd_search(pattern, limit=1)
    if not hits:
        return ""
    first = hits[0]
    return first["coordinates"] if isinstance(first, dict) else str(first)


# --------------------------------------------------------------------------- #
# Public function                                                             #
# --------------------------------------------------------------------------- #
def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    compiled_vals, ns_vals, name_vals = [], [], []
    compiled_coords, ns_coords, name_coords = [], [], []

    for _, row in df.iterrows():
        # --------- 0. compiled ---------------------------------------------
        c_coord = _compile_coord(row)
        compiled_coords.append(c_coord)
        compiled_vals.append(_enrich_coord(c_coord))

        # --------- 1. namespace search -------------------------------------
        ns_pattern = str(row.get("namespace", "")).strip()
        ns_coord = (
            _first_coord_from_search(ns_pattern)
            if ns_pattern and ns_pattern != "-"
            else ""
        )
        ns_coords.append(ns_coord)
        ns_vals.append(_enrich_coord(ns_coord))

        # --------- 2. name search ------------------------------------------
        name_pattern = str(row.get("name", "")).strip()
        nm_coord = _first_coord_from_search(name_pattern) if name_pattern else ""
        name_coords.append(nm_coord)
        name_vals.append(_enrich_coord(nm_coord))

    # Build DataFrames for each result set
    compiled_df = pd.DataFrame(compiled_vals).add_prefix("compiled_")
    ns_df = pd.DataFrame(ns_vals).add_prefix("ns_")
    name_df = pd.DataFrame(name_vals).add_prefix("name_")

    enriched = pd.concat(
        [
            df.reset_index(drop=True),
            compiled_df,
            ns_df,
            name_df,
        ],
        axis=1,
    )

    # Insert coordinate columns for reference
    enriched.insert(0, "compiled_coord", compiled_coords)
    enriched.insert(1, "ns_coord", ns_coords)
    enriched.insert(2, "name_coord", name_coords)

    return enriched
