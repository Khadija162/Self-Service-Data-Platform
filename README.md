# Self-Service Data Platform

An open-source **local self-service data product portal prototype** with domain-owned sales/inventory data products, contract validation, Bronze/Silver/Gold Parquet ETL, a catalog API, request-for-review workflow, Streamlit frontend, optional open-weight LLM review, Docker, pytest, CI and Azure infrastructure starter.

> **Scope:** This is a review-first research demonstration. A data product request is recorded **in memory only**; it does not create infrastructure, execute arbitrary code, approve access or deploy pipelines. No Azure resources have been provisioned, and CI/Docker runtime success is not yet independently verified.

## Architecture

```text
Open CC0 sales.csv, inventory.csv -> offline Python domain contracts
                                            |
                                 Bronze raw Parquet
                                 Silver valid/rejected
                                 Gold product aggregates
                                            |
                                   JSON product catalog
                                            |
                       FastAPI: catalog / requests / AI review
                                            |
                               Streamlit self-service portal
                         Docker Compose, pytest, GitHub Actions
```

## Open data

The repository includes original **CC0 synthetic fixtures**: [sales.csv](data/public/sales.csv) (8 orders) and [inventory.csv](data/public/inventory.csv) (6 products). They do not represent real commerce data or customers. See [dataset attribution](data/public/README.md).

## Windows PowerShell setup

```powershell
git clone https://github.com/Khadija162/Self-Service-Data-Platform.git
cd Self-Service-Data-Platform
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m platform_core.pipeline
.\.venv\Scripts\python.exe -m pytest -q
```

The pipeline generates independently validated Sales and Inventory Parquet layers and writes `artifacts/catalog.json`.

Start the backend and frontend in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

Or, **after building the catalog**, run Docker Desktop:

```powershell
docker compose up --build
```

- API documentation: http://localhost:8000/docs
- Self-service portal: http://localhost:8501

The API reads the catalog from a read-only host-mounted volume; it does not run user-submitted ETL. Requests are not persisted across container restarts.

## Backend endpoints

| Endpoint | Behavior |
|---|---|
| `GET /health` | Health and catalog availability |
| `GET /api/catalog` | Discover data products and their quality status |
| `GET /api/requests` | View review-queue requests |
| `POST /api/requests` | Record a review-only request (sales or inventory) |
| `POST /api/ai/review` | Explain catalog quality using mock or Ollama |

## Open-weight AI

Default `LLM_MODE=mock` gives deterministic read-only feedback. For a locally hosted open-weight model, install [Ollama](https://ollama.com/), pull Qwen and run the host-side backend:

```powershell
ollama pull qwen2.5:3b
$env:LLM_MODE="ollama"
$env:OLLAMA_MODEL="qwen2.5:3b"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

The default Docker Compose app remains in mock mode. AI responses do not grant approval or execute changes.

## Cloud blueprint and limitations

Target architecture: Azure Data Factory/Event Hubs ingestion -> ADLS Gen2 Bronze/Silver/Gold -> Azure Databricks Delta data products -> Microsoft Purview catalog -> Microsoft Entra ID permissions and managed identities -> Container Apps FastAPI/frontend -> PostgreSQL durable requests and workflows -> Azure Monitor/Key Vault. The included Terraform is an **Azure resource group and ADLS Gen2 starter only**, not a live deployment.

This demo is **not production self-service provisioning**. It does not include authentication, tenancy boundaries, durable approvals, governance enforcement, scheduling, quota/budget controls or cloud authorization. Never expose the current unauthenticated API publicly. See [architecture roadmap](docs/architecture.md).

## Status

Files have been committed to GitHub; successful CI/test runs and Docker deployment have not yet been independently verified. No cloud resources have been created.
