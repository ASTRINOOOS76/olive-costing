import os
from datetime import date
import pandas as pd
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "change-me-now")

PIPELINE_STAGES = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
TASK_STATUS = ["Open", "In Progress", "Done", "Blocked"]
ACTIVITY_TYPES = ["Call", "Email", "Meeting", "Note", "Task", "WhatsApp", "Other"]

def api_get(path, params=None):
    r = requests.get(f"{API_BASE}{path}", params=params or {}, headers={"X-API-Key": API_KEY}, timeout=30)
    if r.status_code >= 400:
        st.error(f"API error {r.status_code}: {r.text}")
        return None
    return r.json()

def api_post(path, payload):
    r = requests.post(f"{API_BASE}{path}", json=payload, headers={"X-API-Key": API_KEY}, timeout=30)
    if r.status_code >= 400:
        st.error(f"API error {r.status_code}: {r.text}")
        return None
    return r.json()

def api_put(path, payload):
    r = requests.put(f"{API_BASE}{path}", json=payload, headers={"X-API-Key": API_KEY}, timeout=30)
    if r.status_code >= 400:
        st.error(f"API error {r.status_code}: {r.text}")
        return None
    return r.json()

def api_delete(path):
    r = requests.delete(f"{API_BASE}{path}", headers={"X-API-Key": API_KEY}, timeout=30)
    if r.status_code >= 400:
        st.error(f"API error {r.status_code}: {r.text}")
        return None
    return r.json()

def to_df(x):
    return pd.DataFrame(x) if x else pd.DataFrame()

def money(x):
    try:
        return f"€{float(x):,.2f}"
    except:
        return "€0.00"

st.set_page_config(page_title="CRM v2", layout="wide")
st.title("CRM v2 (FastAPI + DB + Streamlit)")
st.caption("API-backed CRM. Αν δεν σηκώνει αυτό, τότε δεν σηκώνει ούτε καφετέρια στη Σταδίου.")

page = st.sidebar.radio("Menu", ["Dashboard", "Companies", "Contacts", "Deals", "Tasks", "Activities"], index=0)
st.sidebar.caption(f"API: {API_BASE}")

if page == "Dashboard":
    kpi = api_get("/kpi")
    if kpi:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Companies", kpi["companies"])
        c2.metric("Contacts", kpi["contacts"])
        c3.metric("Deals", kpi["deals"])
        c4.metric("Open Tasks", kpi["open_tasks"])

        a, b = st.columns(2)
        a.metric("Pipeline (Total)", money(kpi["pipeline_total"]))
        b.metric("Pipeline (Weighted)", money(kpi["pipeline_weighted"]))

    st.subheader("Deals by Stage")
    deals = api_get("/deals", params={"stage": "All"})
    df = to_df(deals)
    if df.empty:
        st.info("No deals yet.")
    else:
        df["weighted"] = df["value_eur"].fillna(0) * (df["probability"].fillna(0)/100.0)
        agg = df.groupby("stage").agg(deals=("id","count"), total=("value_eur","sum"), weighted=("weighted","sum")).reset_index()
        st.dataframe(agg, use_container_width=True)
        st.bar_chart(agg.set_index("stage")["total"])

elif page == "Companies":
    st.subheader("List")
    q = st.text_input("Search", "")
    data = api_get("/companies", params={"q": q})
    df = to_df(data)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "companies.csv", "text/csv")

    st.divider()
    st.subheader("Add / Update / Delete")
    mode = st.radio("Mode", ["Add", "Update", "Delete"], horizontal=True)
    companies = api_get("/companies", params={"q": ""}) or []
    opts = {f'{c["name"]} (#{c["id"]})': c["id"] for c in companies}

    sel_id = None
    if mode != "Add" and opts:
        sel_label = st.selectbox("Select company", list(opts.keys()))
        sel_id = opts[sel_label]

    name = st.text_input("Name *")
    country = st.text_input("Country")
    city = st.text_input("City")
    vat = st.text_input("VAT/NIP")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    website = st.text_input("Website")
    notes = st.text_area("Notes", height=120)

    payload = dict(name=name, country=country, city=city, vat=vat, email=email, phone=phone, website=website, notes=notes)

    col1, col2, col3 = st.columns(3)
    if col1.button("Execute"):
        if mode == "Add":
            api_post("/companies", payload)
        elif mode == "Update":
            if sel_id:
                api_put(f"/companies/{sel_id}", payload)
        else:
            if sel_id:
                api_delete(f"/companies/{sel_id}")

elif page == "Contacts":
    st.subheader("List")
    companies = api_get("/companies", params={"q": ""}) or []
    comp_map = {"All": None} | {f'{c["name"]} (#{c["id"]})': c["id"] for c in companies}
    comp_sel = st.selectbox("Company filter", list(comp_map.keys()))
    company_id = comp_map[comp_sel]

    q = st.text_input("Search contact", "")
    params = {"q": q}
    if company_id:
        params["company_id"] = company_id
    data = api_get("/contacts", params=params)
    df = to_df(data)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "contacts.csv", "text/csv")

    st.divider()
    st.subheader("Add / Update / Delete")
    mode = st.radio("Mode", ["Add", "Update", "Delete"], horizontal=True, key="ct_mode")

    contacts = api_get("/contacts", params={"q": ""}) or []
    opts = {f'{(c.get("first_name") or "")} {(c.get("last_name") or "")} — {c.get("email") or ""} (#{c["id"]})': c["id"] for c in contacts}
    sel_id = None
    if mode != "Add" and opts:
        sel_label = st.selectbox("Select contact", list(opts.keys()))
        sel_id = opts[sel_label]

    company_id2 = st.selectbox("Company (optional)", ["None"] + [f'{c["name"]} (#{c["id"]})' for c in companies])
    company_id2 = None if company_id2 == "None" else int(company_id2.split("#")[-1].rstrip(")"))

    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    title = st.text_input("Title/Role")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    linkedin = st.text_input("LinkedIn")
    notes = st.text_area("Notes", height=120)

    payload = dict(company_id=company_id2, first_name=first_name, last_name=last_name, title=title, email=email, phone=phone, linkedin=linkedin, notes=notes)

    if st.button("Execute", key="ct_exec"):
        if mode == "Add":
            api_post("/contacts", payload)
        elif mode == "Update":
            if sel_id:
                api_put(f"/contacts/{sel_id}", payload)
        else:
            if sel_id:
                api_delete(f"/contacts/{sel_id}")

elif page == "Deals":
    st.subheader("List")
    q = st.text_input("Search deal", "")
    stage = st.selectbox("Stage", ["All"] + PIPELINE_STAGES)
    data = api_get("/deals", params={"q": q, "stage": stage})
    df = to_df(data)
    if not df.empty:
        df["weighted"] = df["value_eur"].fillna(0) * (df["probability"].fillna(0)/100.0)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "deals.csv", "text/csv")

    st.divider()
    st.subheader("Add / Update / Delete")
    mode = st.radio("Mode", ["Add", "Update", "Delete"], horizontal=True, key="deal_mode")
    deals = api_get("/deals", params={"stage": "All"}) or []
    opts = {f'{d["title"]} [{d["stage"]}] (#{d["id"]})': d["id"] for d in deals}
    sel_id = None
    if mode != "Add" and opts:
        sel_label = st.selectbox("Select deal", list(opts.keys()))
        sel_id = opts[sel_label]

    companies = api_get("/companies", params={"q": ""}) or []
    company_id = st.selectbox("Company (optional)", ["None"] + [f'{c["name"]} (#{c["id"]})' for c in companies])
    company_id = None if company_id == "None" else int(company_id.split("#")[-1].rstrip(")"))

    title = st.text_input("Deal title *")
    stage2 = st.selectbox("Stage *", PIPELINE_STAGES)
    value = st.number_input("Value (€)", min_value=0.0, value=0.0, step=100.0)
    prob = st.number_input("Probability (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
    close = st.date_input("Expected close date", value=None)
    source = st.text_input("Source")
    owner = st.text_input("Owner")
    notes = st.text_area("Notes", height=120)

    payload = dict(
        company_id=company_id, title=title, stage=stage2, value_eur=float(value), probability=float(prob),
        expected_close_date=(close.isoformat() if isinstance(close, date) else None),
        source=source, owner=owner, notes=notes
    )

    if st.button("Execute", key="deal_exec"):
        if mode == "Add":
            api_post("/deals", payload)
        elif mode == "Update":
            if sel_id:
                api_put(f"/deals/{sel_id}", payload)
        else:
            if sel_id:
                api_delete(f"/deals/{sel_id}")

elif page == "Tasks":
    st.subheader("List")
    status = st.selectbox("Status", ["All"] + TASK_STATUS)
    owner = st.text_input("Owner filter", "")
    due_before = st.date_input("Due on/before", value=None)

    params = {"status": status, "owner": owner}
    if isinstance(due_before, date):
        params["due_before"] = due_before.isoformat()

    data = api_get("/tasks", params=params)
    df = to_df(data)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "tasks.csv", "text/csv")

    st.divider()
    st.subheader("Add / Update / Delete")
    mode = st.radio("Mode", ["Add", "Update", "Delete"], horizontal=True, key="task_mode")
    tasks = api_get("/tasks", params={"status": "All"}) or []
    opts = {f'#{t["id"]} {t["title"]} [{t["status"]}]': t["id"] for t in tasks}
    sel_id = None
    if mode != "Add" and opts:
        sel_label = st.selectbox("Select task", list(opts.keys()))
        sel_id = opts[sel_label]

    title = st.text_input("Title *")
    due = st.date_input("Due date", value=None, key="task_due")
    status2 = st.selectbox("Status *", TASK_STATUS, key="task_status")
    priority = st.selectbox("Priority", [1,2,3], index=1, format_func=lambda x: {1:"1-High",2:"2-Normal",3:"3-Low"}[x])
    owner2 = st.text_input("Owner", key="task_owner")
    notes = st.text_area("Notes", height=120, key="task_notes")

    payload = dict(
        title=title,
        due_date=(due.isoformat() if isinstance(due, date) else None),
        status=status2,
        priority=int(priority),
        owner=owner2,
        notes=notes
    )

    if st.button("Execute", key="task_exec"):
        if mode == "Add":
            api_post("/tasks", payload)
        elif mode == "Update":
            if sel_id:
                api_put(f"/tasks/{sel_id}", payload)
        else:
            if sel_id:
                api_delete(f"/tasks/{sel_id}")

elif page == "Activities":
    st.subheader("List")
    q = st.text_input("Search activity", "")
    days = st.number_input("Lookback days", min_value=1, max_value=3650, value=30, step=10)

    data = api_get("/activities", params={"q": q, "days": int(days)})
    df = to_df(data)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "activities.csv", "text/csv")

    st.divider()
    st.subheader("Add / Delete")
    mode = st.radio("Mode", ["Add", "Delete"], horizontal=True, key="act_mode")

    sel_id = None
    if mode == "Delete" and not df.empty:
        opts = {f'#{r["id"]} {r["activity_date"]} {r["activity_type"]} {r.get("subject","") or ""}': r["id"] for _, r in df.head(500).iterrows()}
        sel_label = st.selectbox("Select activity", list(opts.keys()))
        sel_id = opts[sel_label]

    a_type = st.selectbox("Type *", ACTIVITY_TYPES)
    a_date = st.date_input("Activity date *", value=date.today())
    subject = st.text_input("Subject")
    body = st.text_area("Body", height=120)

    payload = dict(activity_type=a_type, activity_date=a_date.isoformat(), subject=subject, body=body)

    if st.button("Execute", key="act_exec"):
        if mode == "Add":
            api_post("/activities", payload)
        else:
            if sel_id:
                api_delete(f"/activities/{sel_id}")
