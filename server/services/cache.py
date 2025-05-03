# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

"""
Very simple in‑memory LRU cache to avoid hammering the Clearly API.
"""

from functools import lru_cache
from clearly import get_definition

@lru_cache(maxsize=2048)
def cached_definition(coord: str):
    return get_definition(coord)
