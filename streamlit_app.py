
# Sales Tree CRM — Streamlit Standalone App
# (No backend API, all logic will be local or in this file)


import streamlit as st
import copy
from datetime import date, datetime

# ── Local API Helper Functions ──
import types

class DummyResponse:
    def __init__(self, data=None, status_code=200, text=None):
        self._data = data
        self.status_code = status_code
        self.text = text or ""
    def json(self):
        return self._data

def api_post(endpoint, payload):
    # Simulate POST: add to session state
    if endpoint == "/companies":
        companies = st.session_state.companies
        new_id = max([c.get("id", 0) for c in companies] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        companies.append(payload)
        return DummyResponse(payload)
    if endpoint == "/contacts":
        contacts = st.session_state.contacts
        new_id = max([c.get("id", 0) for c in contacts] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        contacts.append(payload)
        return DummyResponse(payload)
    if endpoint == "/deals":
        deals = st.session_state.deals
        new_id = max([d.get("id", 0) for d in deals] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        deals.append(payload)
        return DummyResponse(payload)
    if endpoint == "/activities":
        activities = st.session_state.activities
        new_id = max([a.get("id", 0) for a in activities] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        activities.append(payload)
        return DummyResponse(payload)
    if endpoint == "/items":
        items = st.session_state.pos
        new_id = max([i.get("id", 0) for i in items] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        items.append(payload)
        return DummyResponse(payload)
    if endpoint == "/quotes":
        quotes = st.session_state.quotes
        new_id = max([q.get("id", 0) for q in quotes] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        quotes.append(payload)
        return DummyResponse(payload)
    if endpoint == "/purchase-orders":
        pos = st.session_state.pos
        new_id = max([p.get("id", 0) for p in pos] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        pos.append(payload)
        return DummyResponse(payload)
    if endpoint == "/pricelists":
        if "pricelists" not in st.session_state:
            st.session_state.pricelists = []
        pls = st.session_state.pricelists
        new_id = max([p.get("id", 0) for p in pls] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        payload["lines"] = []
        pls.append(payload)
        return DummyResponse(payload)
    if endpoint == "/emails/send":
        if "emails" not in st.session_state:
            st.session_state.emails = []
        emails = st.session_state.emails
        new_id = max([e.get("id", 0) for e in emails] or [0]) + 1
        payload = dict(payload)
        payload["id"] = new_id
        payload["direction"] = "out"
        emails.append(payload)
        return DummyResponse(payload)
    return DummyResponse({}, 404, "Not implemented")

def api_get(endpoint, params=None):
    # Simulate GET: fetch from session state
    if endpoint == "/companies":
        companies = st.session_state.companies
        if params:
            if params.get("is_customer"):
                companies = [c for c in companies if c.get("is_customer")]
            if params.get("is_supplier"):
                companies = [c for c in companies if c.get("is_supplier")]
        return DummyResponse(companies)
    if endpoint == "/contacts":
        return DummyResponse(st.session_state.contacts)
    if endpoint == "/deals":
        return DummyResponse(st.session_state.deals)
    if endpoint == "/activities":
        return DummyResponse(st.session_state.activities)
    if endpoint == "/items":
        return DummyResponse(st.session_state.pos)
    if endpoint == "/quotes":
        return DummyResponse(st.session_state.quotes)
    if endpoint == "/purchase-orders":
        return DummyResponse(st.session_state.pos)
    if endpoint == "/pricelists":
        return DummyResponse(getattr(st.session_state, "pricelists", []))
    if endpoint == "/emails":
        return DummyResponse(getattr(st.session_state, "emails", []))
    if endpoint.startswith("/pricelists/") and endpoint.endswith("/lines"):
        pl_id = int(endpoint.split("/")[2])
        pls = getattr(st.session_state, "pricelists", [])
        for pl in pls:
            if pl["id"] == pl_id:
                return DummyResponse(pl.get("lines", []))
        return DummyResponse([])
    return DummyResponse({}, 404, "Not implemented")

def api_delete(endpoint):
    # Simulate DELETE: remove from session state
    if endpoint.startswith("/companies/"):
        cid = int(endpoint.split("/")[2])
        st.session_state.companies = [c for c in st.session_state.companies if c["id"] != cid]
        return DummyResponse({}, 200)
    if endpoint.startswith("/contacts/"):
        cid = int(endpoint.split("/")[2])
        st.session_state.contacts = [c for c in st.session_state.contacts if c["id"] != cid]
        return DummyResponse({}, 200)
    if endpoint.startswith("/deals/"):
        did = int(endpoint.split("/")[2])
        st.session_state.deals = [d for d in st.session_state.deals if d["id"] != did]
        return DummyResponse({}, 200)
    if endpoint.startswith("/items/"):
        iid = int(endpoint.split("/")[2])
        st.session_state.pos = [i for i in st.session_state.pos if i["id"] != iid]
        return DummyResponse({}, 200)
    if endpoint.startswith("/pricelists/"):
        plid = int(endpoint.split("/")[2])
        pls = getattr(st.session_state, "pricelists", [])
        st.session_state.pricelists = [pl for pl in pls if pl["id"] != plid]
        return DummyResponse({}, 200)
    return DummyResponse({}, 404, "Not implemented")

def api_patch(endpoint, payload=None):
    # Simulate PATCH: update in session state
    if endpoint.startswith("/deals/") and endpoint.endswith("/stage"):
        did = int(endpoint.split("/")[2])
        for d in st.session_state.deals:
            if d["id"] == did:
                d["stage"] = payload["stage"]
                return DummyResponse(d)
        return DummyResponse({}, 404, "Not found")
    if endpoint.startswith("/activities/") and endpoint.endswith("/complete"):
        aid = int(endpoint.split("/")[2])
        for a in st.session_state.activities:
            if a["id"] == aid:
                a["completed_at"] = datetime.now().isoformat()
                return DummyResponse(a)
        return DummyResponse({}, 404, "Not found")
    return DummyResponse({}, 404, "Not implemented")

def api_headers():
    return {}

# Dummy API base for PDF download simulation
API = "http://localhost:8000"

# Dummy requests for PDF download simulation
class requests:
    @staticmethod
    def get(url, headers=None, timeout=30):
        # Simulate PDF download: always fail (no backend)
        class DummyPDF:
            status_code = 404
            content = b""
        return DummyPDF()

# ── Config ───────────────────────────────────────────────────


st.set_page_config(
    page_title="Sales Tree CRM",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .block-container {padding-top: 1rem;}
    div.stButton > button {width: 100%; border-radius: 6px; height: 42px; font-weight: 600;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 10px; color: white; text-align: center;
    }
    .metric-card h2 {margin: 0; font-size: 2rem;}
    .metric-card p {margin: 0; opacity: 0.8;}
    .status-badge {
        display: inline-block; padding: 2px 10px; border-radius: 12px;
        font-size: 0.8em; font-weight: 600;
    }
    .stage-lead {background: #e3f2fd; color: #1565c0;}
    .stage-qualified {background: #fff3e0; color: #e65100;}
    .stage-proposal {background: #f3e5f5; color: #7b1fa2;}
    .stage-negotiation {background: #fce4ec; color: #c62828;}
    .stage-won {background: #e8f5e9; color: #2e7d32;}
    .stage-lost {background: #efebe9; color: #4e342e;}
</style>
""", unsafe_allow_html=True)


# ── Session State ────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "tenant_id" not in st.session_state:
    st.session_state.tenant_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None



if "companies" not in st.session_state:
    st.session_state.companies = []
if "contacts" not in st.session_state:
    st.session_state.contacts = []
if "deals" not in st.session_state:
    st.session_state.deals = []
if "activities" not in st.session_state:
    st.session_state.activities = []
if "quotes" not in st.session_state:
    st.session_state.quotes = []
if "pos" not in st.session_state:
    st.session_state.pos = []



def auth_screen():
    pass  # Login/registration removed; app is fully local now.


# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown("## 📊 Dashboard")

    companies = st.session_state.companies
    contacts = st.session_state.contacts
    deals = st.session_state.deals
    activities = st.session_state.activities
    quotes = st.session_state.quotes
    pos = st.session_state.pos

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("Companies", len(companies))
    with c2:
        st.metric("Contacts", len(contacts))
    with c3:
        st.metric("Deals", len(deals))
    with c4:
        st.metric("Activities", len(activities))
    with c5:
        st.metric("Quotes", len(quotes))
    with c6:
        st.metric("POs", len(pos))

    st.markdown("---")

    # Pipeline summary
    if deals:
        deal_list = deals
        if deal_list:
            st.markdown("### 🎯 Pipeline Overview")
            stages = ["lead", "qualified", "proposal", "negotiation", "won", "lost"]
            cols = st.columns(len(stages))
            for i, stage in enumerate(stages):
                count = len([d for d in deal_list if d.get("stage") == stage])
                value = sum(d.get("value") or 0 for d in deal_list if d.get("stage") == stage)
                with cols[i]:
                    st.markdown(f"**{stage.upper()}**")
                    st.markdown(f"🔢 {count} deals")
                    st.markdown(f"💰 €{value:,.2f}")

    # Recent activities
    if activities:
        act_list = activities[:5]
        if act_list:
            st.markdown("### 📋 Recent Activities")
            for a in act_list:
                icon = {"task": "📌", "call": "📞", "meeting": "🤝", "email": "📧"}.get(a.get("activity_type", ""), "📌")
                done = "✅" if a.get("completed_at") else "⬜"
                st.markdown(f"{done} {icon} **{a['subject']}** — {a.get('activity_type', '')}")


# ══════════════════════════════════════════════════════════════
# COMPANIES
# ══════════════════════════════════════════════════════════════
def page_companies():
    st.markdown("## 🏢 Companies")

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        with st.form("add_company"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Company Name *")
                vat = st.text_input("VAT Number")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            with col2:
                country = st.text_input("Country Code (e.g. GR)", max_chars=2)
                address = st.text_area("Address")
                is_customer = st.checkbox("Customer", value=True)
                is_supplier = st.checkbox("Supplier", value=False)

            if st.form_submit_button("Create Company", type="primary"):
                if not name:
                    st.error("Name is required")
                else:
                    r = api_post("/companies", {
                        "name": name, "vat": vat or None, "email": email or None,
                        "phone": phone or None, "country": country or None,
                        "address": address or None,
                        "is_customer": is_customer, "is_supplier": is_supplier
                    })
                    if r and r.status_code == 200:
                        st.success(f"Company '{name}' created!")
                        st.rerun()
                    elif r:
                        st.error(r.text)

    with tab_list:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            f_type = st.selectbox("Filter", ["All", "Customers", "Suppliers"])
        params = {}
        if f_type == "Customers":
            params["is_customer"] = True
        elif f_type == "Suppliers":
            params["is_supplier"] = True

        r = api_get("/companies", params)
        if r and r.status_code == 200:
            companies = r.json()
            if not companies:
                st.info("No companies yet. Add one!")
            else:
                for c in companies:
                    tags = []
                    if c.get("is_customer"):
                        tags.append("🟢 Customer")
                    if c.get("is_supplier"):
                        tags.append("🔵 Supplier")
                    tag_str = " | ".join(tags)

                    with st.expander(f"**{c['name']}** — {tag_str} {('| VAT: ' + c['vat']) if c.get('vat') else ''}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"📧 {c.get('email', '-')}")
                            st.write(f"📞 {c.get('phone', '-')}")
                        with col2:
                            st.write(f"🌍 {c.get('country', '-')}")
                            st.write(f"📍 {c.get('address', '-')}")
                        with col3:
                            if st.button("🗑️ Delete", key=f"del_co_{c['id']}"):
                                dr = api_delete(f"/companies/{c['id']}")
                                if dr and dr.status_code == 200:
                                    st.success("Deleted")
                                    st.rerun()


# ══════════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════════
def page_contacts():
    st.markdown("## 👤 Contacts")

    # Load companies for dropdown
    r_co = api_get("/companies")
    companies = r_co.json() if r_co and r_co.status_code == 200 else []
    co_map = {c["id"]: c["name"] for c in companies}

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        if not companies:
            st.warning("Create a company first.")
        else:
            with st.form("add_contact"):
                col1, col2 = st.columns(2)
                with col1:
                    company_idx = st.selectbox("Company *", range(len(companies)),
                                               format_func=lambda i: companies[i]["name"])
                    first_name = st.text_input("First Name")
                    last_name = st.text_input("Last Name")
                with col2:
                    email = st.text_input("Email")
                    phone = st.text_input("Phone")
                    position = st.text_input("Position")

                if st.form_submit_button("Create Contact", type="primary"):
                    r = api_post("/contacts", {
                        "company_id": companies[company_idx]["id"],
                        "first_name": first_name or None,
                        "last_name": last_name or None,
                        "email": email or None,
                        "phone": phone or None,
                        "position": position or None,
                    })
                    if r and r.status_code == 200:
                        st.success("Contact created!")
                        st.rerun()
                    elif r:
                        st.error(r.text)

    with tab_list:
        r = api_get("/contacts")
        if r and r.status_code == 200:
            contacts = r.json()
            if not contacts:
                st.info("No contacts yet.")
            else:
                for ct in contacts:
                    co_name = co_map.get(ct.get("company_id"), "—")
                    name = f"{ct.get('first_name', '')} {ct.get('last_name', '')}".strip() or "—"
                    with st.expander(f"**{name}** — {co_name}"):
                        st.write(f"📧 {ct.get('email', '-')} | 📞 {ct.get('phone', '-')} | 💼 {ct.get('position', '-')}")
                        if st.button("🗑️ Delete", key=f"del_ct_{ct['id']}"):
                            dr = api_delete(f"/contacts/{ct['id']}")
                            if dr and dr.status_code == 200:
                                st.rerun()


# ══════════════════════════════════════════════════════════════
# DEALS / PIPELINE
# ══════════════════════════════════════════════════════════════
def page_deals():
    st.markdown("## 🎯 Deals & Pipeline")

    r_co = api_get("/companies")
    companies = r_co.json() if r_co and r_co.status_code == 200 else []
    co_map = {c["id"]: c["name"] for c in companies}

    STAGES = ["lead", "qualified", "proposal", "negotiation", "won", "lost"]

    tab_pipeline, tab_list, tab_add = st.tabs(["🔀 Pipeline", "📋 List", "➕ Add"])

    with tab_add:
        if not companies:
            st.warning("Create a company first.")
        else:
            with st.form("add_deal"):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input("Deal Title *")
                    company_idx = st.selectbox("Company *", range(len(companies)),
                                               format_func=lambda i: companies[i]["name"])
                    stage = st.selectbox("Stage", STAGES)
                with col2:
                    value = st.number_input("Value (€)", min_value=0.0, step=100.0)
                    expected_close = st.date_input("Expected Close", value=None)
                    notes = st.text_area("Notes")

                if st.form_submit_button("Create Deal", type="primary"):
                    if not title:
                        st.error("Title required")
                    else:
                        payload = {
                            "company_id": companies[company_idx]["id"],
                            "title": title,
                            "stage": stage,
                            "value": value if value > 0 else None,
                            "notes": notes or None,
                        }
                        if expected_close:
                            payload["expected_close"] = expected_close.isoformat()
                        r = api_post("/deals", payload)
                        if r and r.status_code == 200:
                            st.success("Deal created!")
                            st.rerun()
                        elif r:
                            st.error(r.text)

    r = api_get("/deals")
    deals = r.json() if r and r.status_code == 200 else []

    with tab_pipeline:
        if not deals:
            st.info("No deals yet.")
        else:
            cols = st.columns(len(STAGES))
            for i, stage in enumerate(STAGES):
                with cols[i]:
                    stage_deals = [d for d in deals if d.get("stage") == stage]
                    total = sum(d.get("value") or 0 for d in stage_deals)
                    st.markdown(f"### {stage.upper()}")
                    st.caption(f"{len(stage_deals)} deals · €{total:,.0f}")
                    st.markdown("---")
                    for d in stage_deals:
                        co_name = co_map.get(d.get("company_id"), "")
                        st.markdown(f"**{d['title']}**")
                        st.caption(f"{co_name} · €{d.get('value') or 0:,.0f}")
                        new_stage = st.selectbox("Move to", STAGES, index=STAGES.index(stage),
                                                 key=f"stage_{d['id']}")
                        if new_stage != stage:
                            pr = api_patch(f"/deals/{d['id']}/stage", {"stage": new_stage})
                            if pr and pr.status_code == 200:
                                st.rerun()
                        st.markdown("---")

    with tab_list:
        if not deals:
            st.info("No deals yet.")
        else:
            for d in deals:
                co_name = co_map.get(d.get("company_id"), "—")
                with st.expander(f"**{d['title']}** — {d['stage'].upper()} · €{d.get('value') or 0:,.0f} · {co_name}"):
                    st.write(f"Expected close: {d.get('expected_close', '-')}")
                    st.write(f"Notes: {d.get('notes', '-')}")
                    if st.button("🗑️ Delete", key=f"del_deal_{d['id']}"):
                        dr = api_delete(f"/deals/{d['id']}")
                        if dr and dr.status_code == 200:
                            st.rerun()


# ══════════════════════════════════════════════════════════════
# ACTIVITIES
# ══════════════════════════════════════════════════════════════
def page_activities():
    st.markdown("## 📋 Activities")

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        with st.form("add_activity"):
            col1, col2 = st.columns(2)
            with col1:
                subject = st.text_input("Subject *")
                activity_type = st.selectbox("Type", ["task", "call", "meeting", "email"])
                description = st.text_area("Description")
            with col2:
                due_date = st.date_input("Due Date", value=None)
                due_time = st.time_input("Due Time")
                entity_type = st.selectbox("Link to", ["—", "company", "contact", "deal", "quote", "po"])
                entity_id = st.text_input("Entity ID (optional)")

            if st.form_submit_button("Create Activity", type="primary"):
                if not subject:
                    st.error("Subject required")
                else:
                    payload = {
                        "subject": subject,
                        "activity_type": activity_type,
                        "description": description or None,
                    }
                    if due_date:
                        dt = datetime.combine(due_date, due_time)
                        payload["due_at"] = dt.isoformat()
                    if entity_type != "—":
                        payload["entity_type"] = entity_type
                        payload["entity_id"] = entity_id or None
                    r = api_post("/activities", payload)
                    if r and r.status_code == 200:
                        st.success("Activity created!")
                        st.rerun()
                    elif r:
                        st.error(r.text)

    with tab_list:
        r = api_get("/activities")
        if r and r.status_code == 200:
            activities = r.json()
            if not activities:
                st.info("No activities yet.")
            else:
                pending = [a for a in activities if not a.get("completed_at")]
                done = [a for a in activities if a.get("completed_at")]

                if pending:
                    st.markdown("### ⬜ Pending")
                    for a in pending:
                        icon = {"task": "📌", "call": "📞", "meeting": "🤝", "email": "📧"}.get(a["activity_type"], "📌")
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"{icon} **{a['subject']}** — {a['activity_type']}")
                            if a.get("due_at"):
                                st.caption(f"Due: {a['due_at'][:16]}")
                        with col2:
                            if st.button("✅ Done", key=f"complete_{a['id']}"):
                                api_patch(f"/activities/{a['id']}/complete")
                                st.rerun()

                if done:
                    st.markdown("### ✅ Completed")
                    for a in done:
                        st.markdown(f"~~{a['subject']}~~ — {a['activity_type']}")


# ══════════════════════════════════════════════════════════════
# ITEMS
# ══════════════════════════════════════════════════════════════
def page_items():
    st.markdown("## 📦 Items / Products")

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name *")
                sku = st.text_input("SKU")
                category = st.text_input("Category")
            with col2:
                unit = st.text_input("Unit", value="pcs")
                vat_rate = st.number_input("VAT Rate (%)", min_value=0.0, max_value=100.0, value=24.0)

            if st.form_submit_button("Create Item", type="primary"):
                if not name:
                    st.error("Name required")
                else:
                    r = api_post("/items", {
                        "name": name, "sku": sku or None,
                        "unit": unit, "vat_rate": vat_rate,
                        "category": category or None,
                    })
                    if r and r.status_code == 200:
                        st.success("Item created!")
                        st.rerun()
                    elif r:
                        st.error(r.text)

    with tab_list:
        r = api_get("/items")
        if r and r.status_code == 200:
            items = r.json()
            if not items:
                st.info("No items yet.")
            else:
                for it in items:
                    with st.expander(f"**{it['name']}** — SKU: {it.get('sku', '-')} | {it['unit']} | VAT: {it.get('vat_rate', 0)}%"):
                        st.write(f"Category: {it.get('category', '-')}")
                        if st.button("🗑️ Delete", key=f"del_item_{it['id']}"):
                            dr = api_delete(f"/items/{it['id']}")
                            if dr and dr.status_code == 200:
                                st.rerun()


# ══════════════════════════════════════════════════════════════
# QUOTES
# ══════════════════════════════════════════════════════════════
def page_quotes():
    st.markdown("## 📄 Quotes")

    r_co = api_get("/companies", {"is_customer": True})
    customers = r_co.json() if r_co and r_co.status_code == 200 else []

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        if not customers:
            st.warning("Create a customer company first.")
        else:
            with st.form("add_quote"):
                col1, col2 = st.columns(2)
                with col1:
                    customer_idx = st.selectbox("Customer *", range(len(customers)),
                                                 format_func=lambda i: customers[i]["name"])
                    quote_number = st.text_input("Quote Number *", value=f"Q-{date.today().strftime('%Y%m%d')}-001")
                with col2:
                    quote_date = st.date_input("Date", value=date.today())
                    currency = st.text_input("Currency", value="EUR", max_chars=3)
                notes = st.text_area("Notes")

                st.markdown("**Lines**")
                num_lines = st.number_input("Number of lines", min_value=1, max_value=20, value=1)
                lines = []
                for i in range(int(num_lines)):
                    st.markdown(f"*Line {i+1}*")
                    lc1, lc2, lc3, lc4 = st.columns(4)
                    with lc1:
                        desc = st.text_input("Description", key=f"ql_desc_{i}")
                    with lc2:
                        qty = st.number_input("Qty", min_value=0.001, value=1.0, key=f"ql_qty_{i}")
                    with lc3:
                        unit = st.text_input("Unit", value="pcs", key=f"ql_unit_{i}")
                    with lc4:
                        price = st.number_input("Unit Price", min_value=0.0, value=0.0, key=f"ql_price_{i}")
                    lines.append({"description": desc, "qty": qty, "unit": unit, "unit_price": price})

                if st.form_submit_button("Create Quote", type="primary"):
                    if not quote_number or not any(l["description"] for l in lines):
                        st.error("Quote number and at least one line description required")
                    else:
                        r = api_post("/quotes", {
                            "customer_id": customers[customer_idx]["id"],
                            "quote_number": quote_number,
                            "quote_date": quote_date.isoformat(),
                            "currency": currency,
                            "notes": notes or None,
                            "lines": [l for l in lines if l["description"]],
                        })
                        if r and r.status_code == 200:
                            st.success("Quote created!")
                            st.rerun()
                        elif r:
                            st.error(r.text)

    with tab_list:
        r = api_get("/quotes")
        if r and r.status_code == 200:
            quotes = r.json()
            co_map = {c["id"]: c["name"] for c in customers}
            if not quotes:
                st.info("No quotes yet.")
            else:
                for q in quotes:
                    co_name = co_map.get(q.get("customer_id"), "—")
                    with st.expander(f"**{q['quote_number']}** — {co_name} · {q['quote_date']} · {q.get('status', 'draft')}"):
                        st.write(f"Currency: {q['currency']} | Notes: {q.get('notes', '-')}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📥 Download PDF", key=f"pdf_q_{q['id']}"):
                                pdf_r = requests.get(f"{API}/quotes/{q['id']}/pdf",
                                                     headers=api_headers(), timeout=30)
                                if pdf_r.status_code == 200:
                                    st.download_button("💾 Save PDF", pdf_r.content,
                                                       f"Quote_{q['quote_number']}.pdf",
                                                       mime="application/pdf",
                                                       key=f"dl_q_{q['id']}")
                                else:
                                    st.error("PDF generation failed")


# ══════════════════════════════════════════════════════════════
# PURCHASE ORDERS
# ══════════════════════════════════════════════════════════════
def page_purchase_orders():
    st.markdown("## 🛒 Purchase Orders")

    r_co = api_get("/companies", {"is_supplier": True})
    suppliers = r_co.json() if r_co and r_co.status_code == 200 else []

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        if not suppliers:
            st.warning("Create a supplier company first.")
        else:
            with st.form("add_po"):
                col1, col2 = st.columns(2)
                with col1:
                    supplier_idx = st.selectbox("Supplier *", range(len(suppliers)),
                                                 format_func=lambda i: suppliers[i]["name"])
                    po_number = st.text_input("PO Number *", value=f"PO-{date.today().strftime('%Y%m%d')}-001")
                with col2:
                    po_date = st.date_input("Date", value=date.today())
                    currency = st.text_input("Currency", value="EUR", max_chars=3)
                notes = st.text_area("Notes")

                st.markdown("**Lines**")
                num_lines = st.number_input("Number of lines", min_value=1, max_value=20, value=1)
                lines = []
                for i in range(int(num_lines)):
                    st.markdown(f"*Line {i+1}*")
                    lc1, lc2, lc3, lc4 = st.columns(4)
                    with lc1:
                        desc = st.text_input("Description", key=f"pol_desc_{i}")
                    with lc2:
                        qty = st.number_input("Qty", min_value=0.001, value=1.0, key=f"pol_qty_{i}")
                    with lc3:
                        unit = st.text_input("Unit", value="pcs", key=f"pol_unit_{i}")
                    with lc4:
                        price = st.number_input("Unit Price", min_value=0.0, value=0.0, key=f"pol_price_{i}")
                    lines.append({"description": desc, "qty": qty, "unit": unit, "unit_price": price})

                if st.form_submit_button("Create PO", type="primary"):
                    if not po_number or not any(l["description"] for l in lines):
                        st.error("PO number and at least one line description required")
                    else:
                        r = api_post("/purchase-orders", {
                            "supplier_id": suppliers[supplier_idx]["id"],
                            "po_number": po_number,
                            "po_date": po_date.isoformat(),
                            "currency": currency,
                            "notes": notes or None,
                            "lines": [l for l in lines if l["description"]],
                        })
                        if r and r.status_code == 200:
                            st.success("PO created!")
                            st.rerun()
                        elif r:
                            st.error(r.text)

    with tab_list:
        r = api_get("/purchase-orders")
        if r and r.status_code == 200:
            pos = r.json()
            su_map = {s["id"]: s["name"] for s in suppliers}
            if not pos:
                st.info("No purchase orders yet.")
            else:
                for po in pos:
                    su_name = su_map.get(po.get("supplier_id"), "—")
                    with st.expander(f"**{po['po_number']}** — {su_name} · {po['po_date']} · {po.get('status', 'draft')}"):
                        st.write(f"Currency: {po['currency']} | Notes: {po.get('notes', '-')}")
                        if st.button("📥 Download PDF", key=f"pdf_po_{po['id']}"):
                            pdf_r = requests.get(f"{API}/purchase-orders/{po['id']}/pdf",
                                                 headers=api_headers(), timeout=30)
                            if pdf_r.status_code == 200:
                                st.download_button("💾 Save PDF", pdf_r.content,
                                                   f"PO_{po['po_number']}.pdf",
                                                   mime="application/pdf",
                                                   key=f"dl_po_{po['id']}")


# ══════════════════════════════════════════════════════════════
# PRICE LISTS
# ══════════════════════════════════════════════════════════════
def page_pricelists():
    st.markdown("## 💰 Price Lists")

    tab_list, tab_add = st.tabs(["📋 List", "➕ Add"])

    with tab_add:
        with st.form("add_pricelist"):
            name = st.text_input("Price List Name *")
            currency = st.text_input("Currency", value="EUR", max_chars=3)
            if st.form_submit_button("Create Price List", type="primary"):
                if not name:
                    st.error("Name required")
                else:
                    r = api_post("/pricelists", {"name": name, "currency": currency})
                    if r and r.status_code == 200:
                        st.success("Price list created!")
                        st.rerun()
                    elif r:
                        st.error(r.text)

    with tab_list:
        r = api_get("/pricelists")
        if r and r.status_code == 200:
            pls = r.json()
            if not pls:
                st.info("No price lists yet.")
            else:
                for pl in pls:
                    with st.expander(f"**{pl['name']}** — {pl['currency']}"):
                        # Show lines
                        lr = api_get(f"/pricelists/{pl['id']}/lines")
                        if lr and lr.status_code == 200:
                            lines = lr.json()
                            if lines:
                                for ln in lines:
                                    st.write(f"Item: {ln['item_id']} · Price: {ln['price']} · MOQ: {ln['moq']}")
                            else:
                                st.caption("No lines yet.")
                        if st.button("🗑️ Delete", key=f"del_pl_{pl['id']}"):
                            dr = api_delete(f"/pricelists/{pl['id']}")
                            if dr and dr.status_code == 200:
                                st.rerun()


# ══════════════════════════════════════════════════════════════
# EMAILS
# ══════════════════════════════════════════════════════════════
def page_emails():
    st.markdown("## 📧 Emails")

    tab_inbox, tab_send = st.tabs(["📥 Log", "✉️ Send"])

    with tab_send:
        with st.form("send_email"):
            to = st.text_input("To (comma separated) *")
            cc = st.text_input("CC (comma separated)")
            subject = st.text_input("Subject *")
            body = st.text_area("Body *")

            if st.form_submit_button("Send Email", type="primary"):
                if not to or not subject or not body:
                    st.error("To, Subject, and Body are required")
                else:
                    r = api_post("/emails/send", {
                        "to": [e.strip() for e in to.split(",")],
                        "cc": [e.strip() for e in cc.split(",")] if cc else None,
                        "subject": subject,
                        "body": body,
                    })
                    if r and r.status_code == 200:
                        st.success("Email sent!")
                        st.rerun()
                    elif r:
                        st.error(f"Failed: {r.text}")

    with tab_inbox:
        r = api_get("/emails")
        if r and r.status_code == 200:
            emails = r.json()
            if not emails:
                st.info("No emails logged yet.")
            else:
                for em in emails:
                    direction = "📤" if em["direction"] == "out" else "📥"
                    with st.expander(f"{direction} **{em.get('subject', '(no subject)')}** — {em.get('recipients', em.get('sender', ''))}"):
                        st.write(f"Direction: {em['direction']}")
                        if em.get("entity_type"):
                            st.write(f"Linked to: {em['entity_type']} / {em.get('entity_id', '-')}")


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
if st.session_state.token is None:
    auth_screen()
else:
    with st.sidebar:
        st.markdown("# 🌳 Sales Tree")
        st.caption(f"User: {st.session_state.user_email}")
        st.caption(f"Tenant: {st.session_state.tenant_id}")
        st.markdown("---")

        page = st.radio("Navigation", [
            "📊 Dashboard",
            "🏢 Companies",
            "👤 Contacts",
            "🎯 Deals",
            "📋 Activities",
            "📦 Items",
            "💰 Price Lists",
            "📄 Quotes",
            "🛒 Purchase Orders",
            "📧 Emails",
        ], label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.token = None
            st.session_state.tenant_id = None
            st.session_state.user_email = None
            st.rerun()

    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "🏢 Companies":
        page_companies()
    elif page == "👤 Contacts":
        page_contacts()
    elif page == "🎯 Deals":
        page_deals()
    elif page == "📋 Activities":
        page_activities()
    elif page == "📦 Items":
        page_items()
    elif page == "💰 Price Lists":
        page_pricelists()
    elif page == "📄 Quotes":
        page_quotes()
    elif page == "🛒 Purchase Orders":
        page_purchase_orders()
    elif page == "📧 Emails":
        page_emails()
