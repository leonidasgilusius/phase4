import streamlit as st
import logging
from pathlib import Path
from db.connection import get_connection
from db.admin import run_sql_script

logger = logging.getLogger(__name__)
st.title("Admin Tools")
conn = get_connection()

st.warning("Danger zone: Running scripts will modify the database.")

root = Path(__file__).resolve().parents[1]
schema_path = root / "schema.sql"
populate_path = root / "populate.sql"

col1, col2 = st.columns(2)
with col1:
    if st.button("Run schema.sql", type="primary"):
        try:
            text = schema_path.read_text(encoding="utf-8")
            run_sql_script(conn, text)
            st.success("schema.sql executed successfully")
        except Exception as e:
            logger.exception("schema run failed")
            st.error(str(e))
with col2:
    if st.button("Run populate.sql"):
        try:
            if populate_path.exists():
                text = populate_path.read_text(encoding="utf-8")
                run_sql_script(conn, text)
                st.success("populate.sql executed successfully")
            else:
                st.warning("populate.sql not found in src/")
        except Exception as e:
            logger.exception("populate run failed")
            st.error(str(e))
