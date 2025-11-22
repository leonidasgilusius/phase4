import streamlit as st
import logging
from db.connection import get_connection
import db.queries as q

logger = logging.getLogger(__name__)
st.title("Dashboard")

days = st.sidebar.number_input("Upcoming trials horizon (days)", min_value=1, max_value=90, value=7, step=1)

try:
    conn = get_connection()
    kpis = q.get_kpis(conn, upcoming_days=int(days))
    col1, col2, col3 = st.columns(3)
    col1.metric("Open Cases", kpis["open_cases"])
    col2.metric("Upcoming Trials", kpis["upcoming_trials"])
    col3.metric("Fees MTD", kpis["total_fees_mtd"])
    st.subheader("Top Specializations by Open Cases")
    st.dataframe(kpis["top_specializations"])
    st.subheader("Upcoming Trials")
    rows = q.get_upcoming_trials(conn, days=int(days))
    st.dataframe(rows)
except Exception as e:
    logger.exception("Error on dashboard")
    st.error(f"Error: {e}")
