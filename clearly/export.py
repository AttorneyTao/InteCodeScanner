# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

# clearly/export.py
"""
Utilities to turn raw API JSON into CSV / HTML for reports.

We isolate pandas + Jinja2 here so core modules stay dependency‑light.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import pandas as pd


# --------------------------------------------------------------------------- #
# Core helpers
# --------------------------------------------------------------------------- #
def to_dataframe(items: List[Dict]) -> pd.DataFrame:
    """
    Flatten a list of nested JSON objects into a *wide* DataFrame.

    We rely on `pandas.json_normalize`, which handles dotted-path columns.
    """
    return pd.json_normalize(items)


def to_csv(df: pd.DataFrame, path: str | Path, *, index: bool = False) -> None:
    """
    Write the DataFrame to CSV.

    CSV is great for spreadsheets or quick diffs.
    """
    df.to_csv(path, index=index)


def to_html(
    df: pd.DataFrame,
    path: str | Path,
    *,
    title: str = "ClearlyDefined export",
    index: bool = False,
) -> None:
    """
    Dump an HTML table—handy for email attachments or static reports.
    """
    html_body = df.to_html(index=index, border=0, classes="table table-striped")
    full_doc = f"<!doctype html><html><head><meta charset=utf-8><title>{title}</title>" \
               f"<style>body{{font-family:sans-serif;margin:2em}}</style></head>" \
               f"<body><h2>{title}</h2>{html_body}</body></html>"
    Path(path).write_text(full_doc, encoding="utf-8")
