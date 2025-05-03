<!--
SPDX-FileCopyrightText: 2025 Ryan TAO

SPDX-License-Identifier: MIT
-->

# 🧩 InteCodeScanner

**InteCodeScanner** is a Python-based tool and web application that consumes the [ClearlyDefined API](https://clearlydefined.io/), processes open source component metadata, and enriches CSV input files with licensing and attribution data.

---

## 🚀 Features

- ✅ Compose ClearlyDefined component coordinates from structured input
- 📡 Query the ClearlyDefined API (with rate-limit handling)
- 📄 Enrich CSV input with:
  - `licensed.declared`
  - `licensed.toolScore.total`
  - `facets.core.attribution.parties`
- 📁 Save enriched results to CSV and JSON
- 🌐 Web interface for interactive uploads and processing (FastAPI)

---

## 📁 Project Structure

InteCodeScanner/
├── clearly/ # Python package: coordinates, client, extractors
├── server/ # FastAPI backend
│ ├── main.py # Entry point for Uvicorn
│ ├── api_routes.py # Web routes (upload & enrich)
│ └── services/ # Enrichment logic
├── tests/ # Unit tests
├── Dockerfile # Container definition
├── docker-compose.yml # Deployment
├── requirements.txt # Python dependencies
└── README.md # You’re here!


---

## 🧪 Getting Started (Local)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd InteCodeScanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 2. Run Backend
uvicorn server.main:app --reload

### 3. Access Web UI
Visit: http://localhost:8000

You can upload a CSV file with the following columns:

type

provider

namespace

name

revision

The result will be downloaded as an enriched CSV.
### Docker Usage
Build and Start
docker compose build
docker compose up

###  Example Input CSV
type,provider,namespace,name,revision
npm,npmjs,-,lodash,4.17.21
npm,npmjs,@fluentui,react-text,9.0.0-alpha.13

### Output CSV Fields (added)
licensed_declared

licensed_toolScore_total

attribution_parties

### TODOs & Ideas
 Add user auth

 Upload curated JSON config for selective fields

 Export enriched results as Excel

 ### License
 MIT License

 ### Maintainers

 Attorney Tao
