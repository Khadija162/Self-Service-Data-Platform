"""Approved local-only catalog build. The web API never executes ETL."""
import json
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd

CONTRACTS={
 "sales":{"required":["order_id","customer_code","amount","status"],"key":"order_id"},
 "inventory":{"required":["sku","warehouse","stock_units","reorder_point"],"key":"sku"}
}
def build(source="data/public", root="data", catalog="artifacts/catalog.json"):
    root=Path(root); result={"generated_at":datetime.now(timezone.utc).isoformat(),"products":[]}
    for domain,contract in CONTRACTS.items():
        frame=pd.read_csv(Path(source)/f"{domain}.csv")
        missing=set(contract["required"])-set(frame.columns)
        if missing:raise ValueError(f"Missing {domain} fields: {sorted(missing)}")
        for layer in ("bronze","silver","gold"):(root/layer/domain).mkdir(parents=True,exist_ok=True)
        frame.to_parquet(root/"bronze"/domain/"records.parquet",index=False)
        valid=frame[contract["key"]].notna()&~frame[contract["key"]].duplicated()
        if domain=="sales":
            valid &= pd.to_numeric(frame["amount"],errors="coerce").ge(0)
            valid &= frame["customer_code"].notna()&frame["status"].isin(["placed","paid","shipped","cancelled"])
        else:
            valid &= pd.to_numeric(frame["stock_units"],errors="coerce").ge(0)
            valid &= pd.to_numeric(frame["reorder_point"],errors="coerce").ge(0)&frame["warehouse"].notna()
        clean=frame.loc[valid].copy()
        clean.to_parquet(root/"silver"/domain/"records.parquet",index=False)
        frame.loc[~valid].to_parquet(root/"silver"/domain/"rejected.parquet",index=False)
        if domain=="sales":
            clean["amount"]=pd.to_numeric(clean["amount"])
            gold=clean.groupby("status",as_index=False).agg(records=("order_id","size"),revenue=("amount","sum"))
        else:
            clean["stock_units"]=pd.to_numeric(clean["stock_units"])
            clean["reorder_point"]=pd.to_numeric(clean["reorder_point"])
            clean["restock"]=clean["stock_units"]<clean["reorder_point"]
            gold=clean.groupby("warehouse",as_index=False).agg(skus=("sku","size"),restock_needed=("restock","sum"))
        gold.to_parquet(root/"gold"/domain/"summary.parquet",index=False)
        result["products"].append({"domain":domain,"name":f"{domain}-summary-v1",
          "owner":f"{domain}-data-team","schema":contract["required"],"license":"CC0",
          "source":f"data/public/{domain}.csv","rows":int(len(frame)),"valid":int(len(clean)),
          "rejected":int((~valid).sum()),"status":"passed" if valid.all() else "review"})
    target=Path(catalog);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
if __name__=="__main__":print(json.dumps(build(),indent=2))
