# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

# clearly/__init__.py
from .coordinates import Coordinate, CoordinateError
from .client import ClearlyDefinedClient, ApiError, RateLimitExceeded
from .resources import get_definition, search, get_definitions_bulk
from .export import to_dataframe, to_csv, to_html
from .extract import select_fields, select_fields_many

__all__ = [
    # core types
    "Coordinate",
    "CoordinateError",
    "ClearlyDefinedClient",
    "ApiError",
    "RateLimitExceeded",
    # high‑level helpers
    "get_definition",
    "search",
    "get_definitions_bulk",
    # export helpers
    "to_dataframe",
    "to_csv",
    "to_html",
    "select_fields",
    "select_fields_many",
]
