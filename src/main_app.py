import streamlit as st
import logging
from config.settings import configure_logging
from db.connection import get_connection

configure_logging()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ItsAllGoodman App", layout="wide", initial_sidebar_state="expanded")

# Sidebar debug toggle
if "debug" not in st.session_state:
    st.session_state["debug"] = False
st.sidebar.checkbox("Debug mode (show SQL)", value=st.session_state["debug"], key="debug")

st.title("ItsAllGoodman App")

try:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT DATABASE() AS db")
        dbname = cur.fetchone()["db"]
    st.success(f"Connected to MySQL database: {dbname}")
except Exception as e:
    logger.exception("DB connection error")
    st.error(f"Database connection error: {e}")

st.write("Use the sidebar pages to navigate through features: Dashboard, Employees & Lawyers, Clients & Cases, Trials & Documents, Transactions & Payments, Associates & Skills, Admin Tools.")
