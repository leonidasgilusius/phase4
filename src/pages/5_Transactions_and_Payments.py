import streamlit as st
import logging
from db.connection import get_connection
from db.queries import list_clients_basic, list_cases_basic, payments_ledger
from db.transaction_ops import record_fee_payment

logger = logging.getLogger(__name__)
st.title("Transactions and Payments")
conn = get_connection()

st.subheader("Record Fee Payment")
with st.form("record_fee"):
    col1, col2, col3 = st.columns(3)
    with col1:
        transaction_id = st.text_input("Transaction ID")
        source_account = st.text_input("Source Account")
        destination_account = st.text_input("Destination Account")
    with col2:
        amount = st.text_input("Amount")
        date_value = st.date_input("Date")
    with col3:
        clients = list_clients_basic(conn)
        client_map = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients}
        client_sel = st.selectbox("Client", list(client_map.keys()))
        cases = list_cases_basic(conn)
        case_sel = st.selectbox("Case Title", cases)
    sub = st.form_submit_button("Record Payment")
    if sub:
        try:
            record_fee_payment(conn, transaction_id, source_account, destination_account, amount, date_value, client_map[client_sel], case_sel)
            st.success("Payment recorded")
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
