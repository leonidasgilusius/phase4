import streamlit as st
import logging
from db.connection import get_connection
from db.queries import list_clients_basic, list_cases_basic, payments_ledger, list_cases_for_client, list_businesses
from db.transaction_ops import record_fee_payment, record_business_fee

logger = logging.getLogger(__name__)
st.title("Transactions and Payments")
conn = get_connection()

st.subheader("Record Fee Payment")
with st.form("record_fee"):
    col1, col2, col3 = st.columns(3)
    with col1:
        source_account = st.text_input("Source Account")
        destination_account = st.text_input("Destination Account")
    with col2:
        amount = st.text_input("Amount")
        date_value = st.date_input("Date")
    with col3:
        clients = list_clients_basic(conn)
        client_map = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients}
        client_sel = st.selectbox("Client", list(client_map.keys()))
        client_id_selected = client_map.get(client_sel)
        cases = list_cases_for_client(conn, client_id_selected) if client_id_selected else []
        case_sel = st.selectbox("Case Title", cases)
    sub = st.form_submit_button("Record Payment")
    if sub:
        try:
            new_tx = record_fee_payment(conn, source_account, destination_account, amount, date_value, client_map[client_sel], case_sel)
            st.success(f"Payment recorded (Transaction {new_tx})")
        except Exception as e:
            logger.exception("record_fee_payment failed")
            st.error(str(e))

st.divider()

st.subheader("Payments Ledger")
colf1, colf2, colf3 = st.columns(3)
clients2 = list_clients_basic(conn)
client_map2 = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients2}
with colf1:
    client_filter = st.selectbox("Client (optional)", [""] + list(client_map2.keys()))
with colf2:
    case_filter = st.selectbox("Case (optional)", [""] + list_cases_basic(conn))
with colf3:
    use_dates2 = st.checkbox("Filter by date range", value=False, key="ledger_dates")
    from_date = st.date_input("From", key="from") if use_dates2 else None
    to_date = st.date_input("To", key="to") if use_dates2 else None
if st.button("Load Ledger"):
    try:
        client_id = client_map2.get(client_filter)
        case_title = case_filter or None
        result = payments_ledger(conn, client_id=client_id, case_title=case_title, date_from=from_date or None, date_to=to_date or None)
        st.metric("Total", result["total"]) 
        st.dataframe(result["rows"]) 
    except Exception as e:
        logger.exception("payments_ledger failed")
        st.error(str(e))

st.divider()

st.subheader("Record Business Fee Payment")
with st.form("record_business_fee"):
    b1, b2, b3 = st.columns(3)
    with b1:
        b_source = st.text_input("Source Account", key="b_src")
        b_dest = st.text_input("Destination Account", key="b_dst")
    with b2:
        b_amount = st.text_input("Amount", key="b_amt")
        b_date = st.date_input("Date", key="b_date")
    with b3:
        businesses = list_businesses(conn)
        biz_map = {f"{r['business_name']} ({r['location']})": (r['business_name'], r['location']) for r in businesses}
        biz_sel = st.selectbox("Business", list(biz_map.keys()) if biz_map else [])
    sub_biz = st.form_submit_button("Record Business Fee", disabled=not biz_map)
    if sub_biz:
        try:
            name, loc = biz_map[biz_sel]
            tx = record_business_fee(conn, b_source, b_dest, b_amount, b_date, name, loc)
            st.success(f"Business fee recorded (Transaction {tx})")
        except Exception as e:
            logger.exception("record_business_fee failed")
            st.error(str(e))
