"""Self-service portal: discover products, submit non-executing requests, review quality."""
import os,requests,pandas as pd,streamlit as st
st.set_page_config(page_title="Self-Service Data Platform",layout="wide")
st.title("Self-Service Data Platform")
st.caption("Product discovery · Contract quality · Reviewed provisioning requests")
api=os.getenv("API_URL","http://localhost:8000")
try:
    r=requests.get(api+"/api/catalog",timeout=8);r.raise_for_status()
    products=r.json()["products"]
except requests.RequestException:products=[]
if products:
    a,b,c=st.columns(3)
    a.metric("Products",len(products))
    b.metric("Healthy",sum(p["status"]=="passed" for p in products))
    c.metric("Rejected rows",sum(p["rejected"] for p in products))
    st.dataframe(pd.DataFrame(products)[["domain","name","owner","rows","valid","rejected","status"]],use_container_width=True)
    if st.button("AI review of catalog"):
        try:
            r=requests.post(api+"/api/ai/review",timeout=100);r.raise_for_status();st.json(r.json())
        except requests.RequestException as e:st.error(str(e))
else:st.info("Build the catalog first with python -m platform_core.pipeline")
st.subheader("Request a data product (review queue only)")
with st.form("request"):
    domain=st.selectbox("Domain",["sales","inventory"])
    description=st.text_area("Use case / requirements")
    submitted=st.form_submit_button("Submit for review")
if submitted:
    try:
        r=requests.post(api+"/api/requests",json={"domain":domain,"description":description},timeout=10)
        r.raise_for_status();st.success("Request recorded for review");st.json(r.json())
    except requests.RequestException as e:st.error(str(e))
