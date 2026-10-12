"""Read-only API and in-memory request demonstration; not an authenticated approval workflow."""
import json,os,uuid
from pathlib import Path
import requests
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from platform_core.ai import analyze
app=FastAPI(title="Self-Service Data Platform",version="0.1.0")
REQUESTS={}
class ProductRequest(BaseModel):
    domain:str=Field(pattern="^(sales|inventory)$")
    description:str=Field(min_length=8,max_length=500)
def catalog():
    path=Path(os.getenv("CATALOG_PATH","artifacts/catalog.json"))
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
@app.get("/health")
def health():return {"status":"ok","catalog_ready":catalog() is not None}
@app.get("/api/catalog")
def products():return {"products":(catalog() or {}).get("products",[])}
@app.get("/api/requests")
def requests_list():return {"requests":list(REQUESTS.values())}
@app.post("/api/requests",status_code=201)
def request_product(request:ProductRequest):
    id=str(uuid.uuid4())
    entry={"id":id,"domain":request.domain,"description":request.description,"status":"pending_review"}
    REQUESTS[id]=entry
    return entry
@app.post("/api/ai/review")
def review():
    current=catalog()
    if not current:raise HTTPException(404,"Build catalog first")
    try:return analyze(current)
    except (requests.RequestException,KeyError,ValueError) as exc:raise HTTPException(502,"LLM unavailable") from exc
