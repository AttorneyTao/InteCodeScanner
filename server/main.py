# SPDX-FileCopyrightText: 2025 Ryan TAO
#
# SPDX-License-Identifier: MIT

"""
server/main.py
==============

Entrypoint for the ClearlyDefined enrichment service.

Run locally:
    python -m uvicorn server.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api_routes import router  # API endpoints (definition, enrich, chart)

# --------------------------------------------------------------------------- #
# FastAPI app                                                                 #
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="ClearlyDefined Enrichment API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)

# Core REST routes
app.include_router(router)

# --------------------------------------------------------------------------- #
# UI assets (new)                                                             #
# --------------------------------------------------------------------------- #
templates = Jinja2Templates(directory="server/templates")
app.mount("/static", StaticFiles(directory="server/static"), name="static")


@app.get("/", tags=["ui"])
def root(request: Request):
    """
    HTML upload page (CSV → enriched table + download link).
    """
    return templates.TemplateResponse("index.html", {"request": request})


# --------------------------------------------------------------------------- #
# Health probe                                                                #
# --------------------------------------------------------------------------- #
@app.get("/healthz", tags=["meta"])
def healthz() -> str:
    return "OK"
