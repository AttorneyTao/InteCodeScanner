# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

import io
from collections import Counter
from typing import Any, List, Dict

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")   # headless backend


def declared_bar_chart(defs: List[Dict[str, Any]]) -> bytes:
    decls = [d.get("licensed", {}).get("declared", "UNKNOWN") for d in defs]
    top = Counter(decls).most_common(10)
    labels, counts = zip(*top)

    plt.figure(figsize=(6, 3 + len(labels) * 0.3))
    plt.barh(list(labels), list(counts))
    plt.xlabel("Count")
    plt.title("Top declared licences")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return buf.read()
