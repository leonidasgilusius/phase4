import streamlit as st
import logging
import os
from db.connection import get_connection
from db.queries import list_cases_basic, list_trials_for_case, list_required_docs_for_trial, list_casefile_docs, document_search, list_clients_basic, list_documents_basic
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
    docs = list_documents_basic(conn)
    doc_map = {f"{r['document_id']} - {r['title']}": r['document_id'] for r in docs}
    document_choice = st.selectbox("Document", list(doc_map.keys()) if doc_map else [])
    document_id = doc_map.get(document_choice) if document_choice else None
    sub2 = st.form_submit_button("Add Required Document", disabled=not (case_sel2 and trial_sel and document_id))
    if sub2:
        try:
            if not document_id:
                st.error("Please select a document")
            else:
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
    d1, d2 = st.columns(2)
    with d1:
        title = st.text_input("Title")
        type_value = st.text_input("Type (optional)")
        create_date = st.date_input("Create Date")
    with d2:
        uploaded = st.file_uploader("Upload file", type=None, accept_multiple_files=False, help="Drag & drop or browse a file to store")
    subd = st.form_submit_button("Create Document")
    if subd:
        try:
            if not uploaded:
                st.error("Please upload a file")
            else:
                upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
                os.makedirs(upload_dir, exist_ok=True)
                safe_name = uploaded.name.replace("..", "_")
                file_path = os.path.join("uploads", safe_name)
                abs_path = os.path.join(upload_dir, safe_name)
                with open(abs_path, "wb") as f:
                    f.write(uploaded.getbuffer())
                file_size_bytes = uploaded.size if hasattr(uploaded, "size") else len(uploaded.getbuffer())
                mime_type = uploaded.type if hasattr(uploaded, "type") else None
                new_id = create_document(conn, title, type_value or None, file_path, file_size_bytes or 0, mime_type or None, create_date)
                st.success(f"Document created with ID {new_id}")
        except Exception as e:
            logger.exception("create_document failed")
            st.error(str(e))

st.subheader("Casefile Attachments")
with st.form("attach_doc_casefile"):
    case_cf = st.selectbox("Case Title", list_cases_basic(conn), key="case_cf")
    trials_cf = [r["trial_date"] for r in list_trials_for_case(conn, case_cf)]
    trial_cf = st.selectbox("Trial Date", trials_cf, key="trial_cf")
    clients = list_clients_basic(conn)
    client_map = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients}
    client_choice = st.selectbox("Client", list(client_map.keys()))
    docs2 = list_documents_basic(conn)
    doc_map2 = {f"{r['document_id']} - {r['title']}": r['document_id'] for r in docs2}
    doc_choice2 = st.selectbox("Document", list(doc_map2.keys()))
    suba = st.form_submit_button("Attach to Casefile", disabled=not (case_cf and trial_cf and client_choice in client_map and doc_choice2 in doc_map2))
    if suba:
        try:
            client_id_cf = client_map.get(client_choice)
            document_id_cf = doc_map2.get(doc_choice2)
            if not all([case_cf, trial_cf, client_id_cf, document_id_cf]):
                st.error("Please select case, trial, client and document")
            else:
                attach_document_to_casefile(conn, case_cf, trial_cf, document_id_cf, client_id_cf)
            st.success("Attached to casefile")
        except Exception as e:
            logger.exception("attach_document_to_casefile failed")
            st.error(str(e))

with st.form("remove_doc_casefile"):
    case_cf2 = st.selectbox("Case Title", list_cases_basic(conn), key="case_cf2")
    trials_cf2 = [r["trial_date"] for r in list_trials_for_case(conn, case_cf2)]
    trial_cf2 = st.selectbox("Trial Date", trials_cf2, key="trial_cf2")
    clients2 = list_clients_basic(conn)
    client_map2 = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients2}
    client_choice2 = st.selectbox("Client", list(client_map2.keys()))
    docs3 = list_documents_basic(conn)
    doc_map3 = {f"{r['document_id']} - {r['title']}": r['document_id'] for r in docs3}
    doc_choice3 = st.selectbox("Document", list(doc_map3.keys()))
    subr = st.form_submit_button("Remove from Casefile", disabled=not (case_cf2 and trial_cf2 and client_choice2 in client_map2 and doc_choice3 in doc_map3))
    if subr:
        try:
            client_id_cf2 = client_map2.get(client_choice2)
            document_id_cf2 = doc_map3.get(doc_choice3)
            if not all([case_cf2, trial_cf2, client_id_cf2, document_id_cf2]):
                st.error("Please select case, trial, client and document")
            else:
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
    clients3 = list_clients_basic(conn)
    client_map3 = {f"{r['client_id']} - {r['first_name']} {r['last_name']}": r['client_id'] for r in clients3}
    client_choice3 = st.selectbox("Client", list(client_map3.keys()))
    subv = st.form_submit_button("Load Casefile Docs", disabled=not (case_view and trial_view and client_choice3 in client_map3))
    if subv:
        try:
            client_view_val = client_map3.get(client_choice3)
            docs = list_casefile_docs(conn, case_view, trial_view, client_view_val)
            st.dataframe(docs)
        except Exception as e:
            logger.exception("list_casefile_docs failed")
            st.error(str(e))
