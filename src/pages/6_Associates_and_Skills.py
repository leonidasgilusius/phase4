import streamlit as st
import logging
from db.connection import get_connection
from db.queries import find_associates, find_criminal_associates_by_skills
from db.transaction_ops import create_associate, mark_criminal_associate, add_skill

logger = logging.getLogger(__name__)
st.title("Associates and Skills")
conn = get_connection()

st.subheader("Create Associate")
with st.form("create_associate"):
    a1, a2, a3 = st.columns(3)
    with a1:
        associate_id = st.text_input("Associate ID")
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
            create_associate(conn, associate_id, name, status, loyalty_score, account_no or None, alias_client_id or None)
            st.success("Associate created")
        except Exception as e:
            logger.exception("create_associate failed")
            st.error(str(e))

st.subheader("Mark Criminal Associate")
with st.form("mark_criminal"):
    associate_id2 = st.text_input("Associate ID")
    codename = st.text_input("Codename")
    sub2 = st.form_submit_button("Mark Criminal")
    if sub2:
        try:
            mark_criminal_associate(conn, associate_id2, codename)
            st.success("Marked as criminal associate")
        except Exception as e:
            logger.exception("mark_criminal_associate failed")
            st.error(str(e))

st.subheader("Add Skill")
with st.form("add_skill"):
    associate_id3 = st.text_input("Associate ID")
    skill_name = st.text_input("Skill Name")
    sub3 = st.form_submit_button("Add Skill")
    if sub3:
        try:
            add_skill(conn, associate_id3, skill_name)
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
skills_csv = st.text_input("Skills (comma-separated)")
require_all = st.checkbox("Require all skills", value=False)
if st.button("Search Criminals"):
    try:
        skills = [s.strip() for s in skills_csv.split(',') if s.strip()]
        rows = find_criminal_associates_by_skills(conn, skills, require_all=require_all)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("find_criminal_associates_by_skills failed")
        st.error(str(e))
