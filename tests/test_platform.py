import pandas as pd
from fastapi.testclient import TestClient
from backend.main import app,REQUESTS
from platform_core.pipeline import build
from platform_core.ai import analyze

def sample(root):
    root.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([{"order_id":1,"customer_code":"X","amount":10,"status":"paid"},
      {"order_id":2,"customer_code":"Y","amount":-1,"status":"paid"}]).to_csv(root/"sales.csv",index=False)
    pd.DataFrame([{"sku":"A","warehouse":"W","stock_units":1,"reorder_point":5}]).to_csv(root/"inventory.csv",index=False)

def test_build(tmp_path):
    sample(tmp_path/"source")
    report=build(str(tmp_path/"source"),str(tmp_path/"data"),str(tmp_path/"catalog.json"))
    assert len(report["products"])==2
    assert report["products"][0]["rejected"]==1

def test_api(monkeypatch,tmp_path):
    sample(tmp_path/"source");catalog=tmp_path/"catalog.json"
    build(str(tmp_path/"source"),str(tmp_path/"data"),str(catalog))
    monkeypatch.setenv("CATALOG_PATH",str(catalog))
    client=TestClient(app)
    assert len(client.get("/api/catalog").json()["products"])==2
    assert client.post("/api/requests",json={"domain":"sales","description":"Need dashboard access"}).status_code==201
    assert client.get("/api/requests").json()["requests"]
    assert client.post("/api/requests",json={"domain":"other","description":"Need dashboard access"}).status_code==422
    REQUESTS.clear()

def test_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE","mock")
    assert analyze({"products":[{"domain":"sales","valid":1,"rejected":0,"status":"passed"}]})["approval_required"]
