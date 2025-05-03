"""
server/api_routes.py
====================

All HTTP endpoints exposed by the FastAPI application.

* /definition/{coord}  – proxy ClearlyDefined GET
* /enrich/csv          – upload CSV → enriched CSV download
* /chart/licenses      – quick bar chart of declared‑license counts

Each route is tagged so it shows up nicely in Swagger (/docs).
"""
from __future__ import annotations

import io
import uuid
from typing import List

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse, Response, StreamingResponse

from clearly.resources import (
    get_definition,
    search as cd_search,
    get_definitions_bulk,
)

from .services.enrich import enrich_dataframe
from .services.viz import declared_bar_chart

router = APIRouter()


# --------------------------------------------------------------------------- #
# 1. Definition proxy                                                         #
# --------------------------------------------------------------------------- #
@router.get("/definition/{coord:path}", tags=["definition"])
def definition_proxy(coord: str):
    """
    Return the ClearlyDefined definition JSON for `coord`.
    """
    try:
        data = get_definition(coord)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(502, f"Upstream error: {exc}") from exc
    return JSONResponse(content=data)


# --------------------------------------------------------------------------- #
# 2. CSV enrichment                                                           #
# --------------------------------------------------------------------------- #
@router.post("/enrich/csv", tags=["enrich"])
async def enrich_csv(file: UploadFile = File(...)):
    """
    Accept a coordinate‑parts CSV → return enriched CSV (declared, toolScore_total, parties).
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only .csv files are accepted")

    try:
        df = pd.read_csv(file.file, dtype=str).fillna("")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"CSV parse error: {exc}") from exc

    try:
        enriched = enrich_dataframe(df)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    # Turn DataFrame -> bytes
    csv_bytes: bytes = enriched.to_csv(index=False).encode()
    buf = io.BytesIO(csv_bytes)

    headers = {
        "Content-Disposition": f'attachment; filename="enriched_{uuid.uuid4().hex}.csv"'
    }
    return StreamingResponse(buf, media_type="text/csv", headers=headers)


# --------------------------------------------------------------------------- #
# 3. Visualization                                                            #
# --------------------------------------------------------------------------- #
@router.get("/chart/licenses", tags=["visualization"])
async def license_chart(pattern: str):
    """
    Build a bar chart of the most common declared licences among components
    that match a search `pattern` (up to 200 hits).
    """
    hits = cd_search(pattern, limit=200)  # list[dict] from ClearlyDefined
    if not hits:
        raise HTTPException(404, "No coordinates match pattern")

    coords: List[str] = [h["coordinates"] for h in hits]
    defs = get_definitions_bulk(coords)

    png_bytes = declared_bar_chart(defs)
    return Response(content=png_bytes, media_type="image/png")
