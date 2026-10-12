# Architecture and scope

Implemented: two original CC0 data sources for sales and inventory, locally executed contract-based Bronze/Silver/Gold Parquet ETL, product catalog JSON with provenance and quality, read-only FastAPI catalog, demo-only in-memory product request review queue (no execution), Streamlit portal, optional read-only Ollama reviewer with mock default, pytest, Docker Compose and CI.

Not implemented: persistence for requests, actual approval actions, self-service infrastructure provisioning, tenant authentication, automated pipeline deployment, enterprise policy governance, lineage, SLA monitoring, production secrets and identity. In-memory requests disappear when the API restarts. The public API must remain localhost-bound.

Azure blueprint (not deployed): Data Factory intake -> ADLS Gen2 data zones -> Azure Databricks Spark/Delta products -> Microsoft Purview catalog, Microsoft Entra ID and managed identities -> FastAPI/Streamlit Azure Container Apps -> durable PostgreSQL request/workflow tracking and Azure Monitor, Key Vault. Terraform covers only resource group and ADLS Gen2 starter.
