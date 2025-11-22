import streamlit as st
import logging
from db.connection import get_connection
from db.queries import (
    find_associates,
    find_criminal_associates_by_skills,
    list_associates_basic,
    list_distinct_skills,
    list_all_skills,
    list_criminal_associates,
)
from db.transaction_ops import create_associate, mark_criminal_associate, add_skill

logger = logging.getLogger(__name__)
st.title("Associates and Skills")
conn = get_connection()

st.subheader("Create Associate")
with st.form("create_associate"):
    a1, a2, a3 = st.columns(3)
    with a1:
        name = st.text_input("Name")
    with a2:
        status = st.selectbox("Status", ["active","dead","missing"])
        loyalty_score = st.number_input("Loyalty Score", min_value=1, max_value=10, value=5, step=1)
    with a3:
        account_no = st.text_input("Account No (optional)")
        alias_client_id = st.text_input("Alias Client ID (optional)")
    sub = st.form_submit_button("Create")
    if sub:
        try:
            new_id = create_associate(conn, name, status, loyalty_score, account_no or None, alias_client_id or None)
            st.success(f"Associate created with ID {new_id}")
        except Exception as e:
            logger.exception("create_associate failed")
            st.error(str(e))

st.subheader("Mark Criminal Associate")
with st.form("mark_criminal"):
    assoc_list = list_associates_basic(conn)
    assoc_map = {f"{r['associate_id']} - {r['name']}": r['associate_id'] for r in assoc_list}
    assoc_sel = st.selectbox("Associate", list(assoc_map.keys()))
    codename = st.text_input("Codename")
    sub2 = st.form_submit_button("Mark Criminal")
    if sub2:
        try:
            mark_criminal_associate(conn, assoc_map[assoc_sel], codename)
            st.success("Marked as criminal associate")
        except Exception as e:
            logger.exception("mark_criminal_associate failed")
            st.error(str(e))

st.subheader("Add Skill")
with st.form("add_skill"):
    assoc_list2 = list_associates_basic(conn)
    assoc_map2 = {f"{r['associate_id']} - {r['name']}": r['associate_id'] for r in assoc_list2}
    assoc_sel2 = st.selectbox("Associate", list(assoc_map2.keys()))
    skill_name = st.text_input("Skill Name")
    sub3 = st.form_submit_button("Add Skill")
    if sub3:
        try:
            add_skill(conn, assoc_map2[assoc_sel2], skill_name)
            st.success("Skill added")
        except Exception as e:
            logger.exception("add_skill failed")
            st.error(str(e))

st.divider()

st.subheader("Find Associates")
colf1, colf2, colf3 = st.columns(3)
with colf1:
    status_filter = st.selectbox("Status", ["", "active","dead","missing"])
with colf2:
    loyalty_min = st.number_input("Loyalty Min", min_value=1, max_value=10, value=1, step=1)
with colf3:
    loyalty_max = st.number_input("Loyalty Max", min_value=1, max_value=10, value=10, step=1)
if st.button("Search Associates"):
    try:
        rows = find_associates(conn, status=status_filter or None, loyalty_min=loyalty_min, loyalty_max=loyalty_max)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("find_associates failed")
        st.error(str(e))

st.subheader("Find Criminal Associates by Skills")
skills_options = list_distinct_skills(conn)
skills_selected = st.multiselect("Skills", skills_options)
require_all = st.checkbox("Require all selected skills", value=False)
if st.button("Search Criminals"):
    try:
        rows = find_criminal_associates_by_skills(conn, skills_selected, require_all=require_all)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("find_criminal_associates_by_skills failed")
        st.error(str(e))

st.divider()

st.subheader("Table View: Skills")
try:
    st.dataframe(list_all_skills(conn))
except Exception as e:
    logger.exception("list_all_skills failed")
    st.error(str(e))

st.subheader("Table View: Criminal Associates")
try:
    st.dataframe(list_criminal_associates(conn))
except Exception as e:
    logger.exception("list_criminal_associates failed")
    st.error(str(e))
