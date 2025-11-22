import streamlit as st
import logging
from db.connection import get_connection
from db.queries import search_clients, get_case_summary, list_lawyers, list_clients_basic, list_cases_basic
from db.transaction_ops import create_client, reassign_client_lawyer, create_case, update_case_status

logger = logging.getLogger(__name__)
st.title("Clients and Cases")
conn = get_connection()

st.subheader("Search Clients")
colq1, colq2, colq3, colq4 = st.columns([2,1,1,1])
with colq1:
    q = st.text_input("Name or Email contains")
with colq2:
    type_filter = st.selectbox("Type", ["", "individual", "business", "cartel-affiliated"])
with colq3:
    lawyers = list_lawyers(conn)
    lawyer_map = {f"{r['bar_number']} - {r['first_name']} {r['last_name']}": r['bar_number'] for r in lawyers}
    lawyer_sel = st.selectbox("Lawyer", [""] + list(lawyer_map.keys()))
    lawyer_val = lawyer_map.get(lawyer_sel)
with colq4:
    limit = st.number_input("Limit", min_value=1, max_value=500, value=50, step=10)
if st.button("Search", type="primary"):
    try:
        rows = search_clients(conn, q or "", type_filter or None, lawyer_val, limit)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("search_clients failed")
        st.error(str(e))

st.divider()

st.subheader("Create Client")
with st.form("create_client_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
    with c2:
        phone = st.text_input("Phone (10 digits)")
        email = st.text_input("Email")
        address = st.text_input("Address")
    with c3:
        type_value = st.selectbox("Type", ["individual","business","cartel-affiliated"])
        date_joined = st.date_input("Date Joined")
        account_no = st.text_input("Account No (optional)")
    lawyer_sel2 = st.selectbox("Assign Lawyer (optional)", [""] + list(lawyer_map.keys()))
    lawyer_assigned = lawyer_map.get(lawyer_sel2)
    sub = st.form_submit_button("Create")
    if sub:
        try:
            new_id = create_client(conn, first_name, last_name, phone, email, address, type_value, date_joined, account_no or None, lawyer_assigned)
            st.success("Client created")
        except Exception as e:
            logger.exception("create_client failed")
            st.error(str(e))

st.divider()

st.subheader("Reassign Client's Lawyer")
clients = list_clients_basic(conn)
client_map = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients}
with st.form("reassign_lawyer"):
    client_sel = st.selectbox("Client", list(client_map.keys()))
    new_lawyer_sel = st.selectbox("New Lawyer", list(lawyer_map.keys()))
    sub2 = st.form_submit_button("Reassign")
    if sub2:
        try:
            reassign_client_lawyer(conn, client_map[client_sel], lawyer_map[new_lawyer_sel])
            st.success("Lawyer reassigned")
        except Exception as e:
            logger.exception("reassign_client_lawyer failed")
            st.error(str(e))

st.divider()

st.subheader("Create Case")
with st.form("create_case"):
    cc1, cc2 = st.columns(2)
    with cc1:
        case_title = st.text_input("Case Title")
        client_sel2 = st.selectbox("Client", list(client_map.keys()))
    with cc2:
        description = st.text_input("Description")
        status = st.selectbox("Status", ["open","closed"], index=0)
    sub3 = st.form_submit_button("Create Case")
    if sub3:
        try:
            create_case(conn, case_title, client_map[client_sel2], description, status)
            st.success("Case created")
        except Exception as e:
            logger.exception("create_case failed")
            st.error(str(e))

st.subheader("Update Case Status")
with st.form("update_case_status"):
    cases = list_cases_basic(conn)
    case_sel = st.selectbox("Case Title", cases)
    new_status = st.selectbox("New Status", ["open","closed"])
    sub4 = st.form_submit_button("Update Status")
    if sub4:
        try:
            update_case_status(conn, case_sel, new_status)
            st.success("Case status updated")
        except Exception as e:
            logger.exception("update_case_status failed")
            st.error(str(e))

st.divider()

st.subheader("Case Summary")
case_for_summary = st.selectbox("Select Case for Summary", [""] + list_cases_basic(conn))
if case_for_summary:
    try:
        summary = get_case_summary(conn, case_for_summary)
        c1, c2, c3 = st.columns(3)
        c1.metric("Status", summary["case"]["status"] if summary["case"] else "-")
        c2.metric("Latest Trial", str(summary["latest_trial"]) if summary["latest_trial"] else "-")
        c3.metric("Total Paid", summary["total_paid"]) 
        st.write("Missing Required Docs:", summary["missing_required_docs"]) 
        st.json(summary["case"])
    except Exception as e:
        logger.exception("get_case_summary failed")
        st.error(str(e))
