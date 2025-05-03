from __future__ import annotations

import pandas as pd
from clearly import Coordinate, get_definition
from .cache import cached_definition as get_def


REQUIRED_COLS = {"type", "provider", "namespace", "name", "revision", "pr"}


def _coord_from_row(row: pd.Series) -> Coordinate:
    return Coordinate.from_parts(
        row["type"],
        row["provider"],
        row["namespace"],
        row["name"],
        row["revision"],
        row.get("pr", None),
    )


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not REQUIRED_COLS.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {', '.join(REQUIRED_COLS)}")

    enriched = df.copy()
    for col in ("declared", "toolScore_total", "parties"):
        if col not in enriched.columns:
            enriched[col] = ""

    for idx, row in enriched.iterrows():
        coord = _coord_from_row(row)
        try:
            data = get_definition(coord)
            lic = data.get("licensed", {})
            enriched.at[idx, "declared"] = lic.get("declared", "")
            enriched.at[idx, "toolScore_total"] = lic.get("toolScore", {}).get(
                "total", ""
            )
            parties = (
                lic.get("facets", {})
                .get("core", {})
                .get("attribution", {})
                .get("parties", [])
            )
            enriched.at[idx, "parties"] = (
                "; ".join(parties) if isinstance(parties, list) else str(parties)
            )
        except Exception:  # noqa: BLE001
            # leave blanks on error
            continue

    return enriched
