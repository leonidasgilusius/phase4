import streamlit as st
import logging
from db.connection import get_connection
from db.queries import list_cases_basic, list_trials_for_case, list_required_docs_for_trial, list_casefile_docs, document_search
from db.transaction_ops import schedule_trial, add_required_document, create_document, attach_document_to_casefile, remove_document_from_casefile

logger = logging.getLogger(__name__)
st.title("Trials and Documents")
conn = get_connection()

st.subheader("Schedule Trial")
with st.form("schedule_trial_form"):
    case_sel = st.selectbox("Case Title", list_cases_basic(conn))
    trial_date = st.date_input("Trial Date")
    sub = st.form_submit_button("Schedule")
    if sub:
        try:
            schedule_trial(conn, case_sel, trial_date)
            st.success("Trial scheduled")
        except Exception as e:
            logger.exception("schedule_trial failed")
            st.error(str(e))

st.divider()

st.subheader("Manage Required Documents")
with st.form("add_required_doc"):
    case_sel2 = st.selectbox("Case Title", list_cases_basic(conn), key="case_req")
    trials = [r["trial_date"] for r in list_trials_for_case(conn, case_sel2)]
    trial_sel = st.selectbox("Trial Date", trials)
    document_id = st.text_input("Document ID")
    sub2 = st.form_submit_button("Add Required Document")
    if sub2:
        try:
            add_required_document(conn, case_sel2, trial_sel, document_id)
            st.success("Required document added")
        except Exception as e:
            logger.exception("add_required_document failed")
            st.error(str(e))

case_sel3 = st.selectbox("View Trial Requirements for Case", [""] + list_cases_basic(conn), key="view_req_case")
if case_sel3:
    trials3 = [r["trial_date"] for r in list_trials_for_case(conn, case_sel3)]
    trial_sel3 = st.selectbox("Trial Date", trials3, key="view_req_date")
    if trial_sel3:
        try:
            req = list_required_docs_for_trial(conn, case_sel3, trial_sel3)
            st.write("Required Docs:")
            st.dataframe(req)
        except Exception as e:
            logger.exception("list_required_docs_for_trial failed")
            st.error(str(e))

st.divider()

st.subheader("Document Repository")
col1, col2, col3 = st.columns(3)
with col1:
    title_like = st.text_input("Title contains")
    type_filter = st.text_input("Type (exact)")
with col2:
    use_dates = st.checkbox("Filter by date range", value=False)
    date_from = st.date_input("Created from") if use_dates else None
with col3:
    date_to = st.date_input("Created to") if use_dates else None
if st.button("Search Docs"):
    try:
        rows = document_search(conn, title_like or None, type_filter or None, date_from, date_to, None)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("document_search failed")
        st.error(str(e))

st.subheader("Create Document")
with st.form("create_document_form"):
    d1, d2, d3 = st.columns(3)
    with d1:
        document_id = st.text_input("Document ID")
        title = st.text_input("Title")
        type_value = st.text_input("Type")
    with d2:
        file_path = st.text_input("File Path (stored path)")
        file_size_bytes = st.text_input("File Size (bytes)")
        mime_type = st.text_input("MIME Type")
    with d3:
        create_date = st.date_input("Create Date")
    subd = st.form_submit_button("Create Document")
    if subd:
        try:
            create_document(conn, document_id, title, type_value or None, file_path, file_size_bytes or 0, mime_type or None, create_date)
            st.success("Document created")
        except Exception as e:
            logger.exception("create_document failed")
            st.error(str(e))

st.subheader("Casefile Attachments")
with st.form("attach_doc_casefile"):
    case_cf = st.selectbox("Case Title", list_cases_basic(conn), key="case_cf")
    trials_cf = [r["trial_date"] for r in list_trials_for_case(conn, case_cf)]
    trial_cf = st.selectbox("Trial Date", trials_cf, key="trial_cf")
    client_id_cf = st.text_input("Client ID")
    document_id_cf = st.text_input("Document ID")
    suba = st.form_submit_button("Attach to Casefile")
    if suba:
        try:
            attach_document_to_casefile(conn, case_cf, trial_cf, document_id_cf, client_id_cf)
            st.success("Attached to casefile")
        except Exception as e:
            logger.exception("attach_document_to_casefile failed")
            st.error(str(e))

with st.form("remove_doc_casefile"):
    case_cf2 = st.selectbox("Case Title", list_cases_basic(conn), key="case_cf2")
    trials_cf2 = [r["trial_date"] for r in list_trials_for_case(conn, case_cf2)]
    trial_cf2 = st.selectbox("Trial Date", trials_cf2, key="trial_cf2")
    client_id_cf2 = st.text_input("Client ID", key="client_cf2")
    document_id_cf2 = st.text_input("Document ID", key="doc_cf2")
    subr = st.form_submit_button("Remove from Casefile")
    if subr:
        try:
            remove_document_from_casefile(conn, case_cf2, trial_cf2, document_id_cf2, client_id_cf2)
            st.success("Removed from casefile")
        except Exception as e:
            logger.exception("remove_document_from_casefile failed")
            st.error(str(e))

st.subheader("View Casefile Documents")
with st.form("view_casefile"):
    case_view = st.selectbox("Case Title", list_cases_basic(conn), key="case_view_cf")
    trials_view = [r["trial_date"] for r in list_trials_for_case(conn, case_view)]
    trial_view = st.selectbox("Trial Date", trials_view, key="trial_view")
    client_view = st.text_input("Client ID")
    subv = st.form_submit_button("Load Casefile Docs")
    if subv:
        try:
            docs = list_casefile_docs(conn, case_view, trial_view, client_view)
            st.dataframe(docs)
        except Exception as e:
            logger.exception("list_casefile_docs failed")
            st.error(str(e))
