import streamlit as st
import logging
from db.connection import get_connection
from db.transaction_ops import create_employee, upgrade_to_lawyer, add_specializations
from db.queries import list_lawyer_caseload

logger = logging.getLogger(__name__)
st.title("Employees and Lawyers")

conn = get_connection()

st.subheader("Create Employee")
with st.form("create_employee"):
    employee_id = st.text_input("Employee ID")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    role = st.selectbox("Role", ["lawyer","paralegal","receptionist","investigator"])
    salary = st.text_input("Salary")
    trust_level = st.number_input("Trust Level (1-10)", min_value=1, max_value=10, value=5, step=1)
    submitted = st.form_submit_button("Create")
    if submitted:
        try:
            create_employee(conn, employee_id, first_name, last_name, role, salary, trust_level)
            st.success("Employee created")
        except Exception as e:
            logger.exception("create_employee failed")
            st.error(f"{e}")

st.subheader("Upgrade To Lawyer")
with st.form("upgrade_lawyer"):
    emp_id = st.text_input("Employee ID")
    bar_num = st.text_input("Bar Number")
    submitted2 = st.form_submit_button("Upgrade")
    if submitted2:
        try:
            upgrade_to_lawyer(conn, emp_id, bar_num)
            st.success("Lawyer created")
        except Exception as e:
            logger.exception("upgrade_to_lawyer failed")
            st.error(f"{e}")

st.subheader("Add Specializations To Lawyer")
with st.form("add_specs"):
    bar_num2 = st.text_input("Lawyer Bar Number")
    specs_csv = st.text_input("Specializations (comma-separated)")
    submitted3 = st.form_submit_button("Add")
    if submitted3:
        try:
            specs = [s.strip() for s in specs_csv.split(",")] if specs_csv else []
            add_specializations(conn, bar_num2, specs)
            st.success("Specializations added")
        except Exception as e:
            logger.exception("add_specializations failed")
            st.error(f"{e}")

st.subheader("View Lawyer Caseload")
bar_lookup = st.text_input("Lawyer Bar Number for Caseload")
if st.button("Load Caseload"):
    try:
        rows = list_lawyer_caseload(conn, bar_lookup)
        st.dataframe(rows)
    except Exception as e:
        logger.exception("list_lawyer_caseload failed")
        st.error(f"{e}")
