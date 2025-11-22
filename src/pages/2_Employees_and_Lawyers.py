import streamlit as st
import logging
from db.connection import get_connection
from db.transaction_ops import create_employee, upgrade_to_lawyer, add_specializations
from db.queries import list_lawyer_caseload, list_employees_basic, list_lawyers

logger = logging.getLogger(__name__)
st.title("Employees and Lawyers")

conn = get_connection()

st.subheader("Create Employee")
with st.form("create_employee"):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    role = st.selectbox("Role", ["lawyer","paralegal","receptionist","investigator"])
    salary = st.text_input("Salary")
    trust_level = st.number_input("Trust Level (1-10)", min_value=1, max_value=10, value=5, step=1)
    bar_num_new = st.text_input("Bar Number (optional; used only when role is lawyer)")
    submitted = st.form_submit_button("Create")
    if submitted:
        try:
            new_id = create_employee(conn, first_name, last_name, role, salary, trust_level)
            if role == "lawyer":
                assigned_bar = upgrade_to_lawyer(conn, new_id, bar_num_new)
                st.success(f"Employee created and promoted to Lawyer with bar number {assigned_bar}")
            else:
                st.success("Employee created")
        except Exception as e:
            logger.exception("create_employee failed")
            st.error(f"{e}")

st.subheader("Upgrade To Lawyer")
with st.form("upgrade_lawyer"):
    emps = list_employees_basic(conn)
    emp_map = {f"{r['employee_id']} - {r['first_name']} {r['last_name']}": r['employee_id'] for r in emps}
    emp_sel = st.selectbox("Employee", list(emp_map.keys()))
    bar_num = st.text_input("Bar Number")
    submitted2 = st.form_submit_button("Upgrade")
    if submitted2:
        try:
            assigned = upgrade_to_lawyer(conn, emp_map[emp_sel], bar_num)
            st.success(f"Lawyer created with bar number {assigned}")
        except Exception as e:
            logger.exception("upgrade_to_lawyer failed")
            st.error(f"{e}")

st.subheader("Add Specializations To Lawyer")
with st.form("add_specs"):
    lawyers = list_lawyers(conn)
    law_map = {f"{r['bar_number']} - {r['first_name']} {r['last_name']}": r['bar_number'] for r in lawyers}
    law_sel = st.selectbox("Lawyer", list(law_map.keys()))
    specs_csv = st.text_input("Specializations (comma-separated)")
    submitted3 = st.form_submit_button("Add")
    if submitted3:
        try:
            specs = [s.strip() for s in specs_csv.split(",")] if specs_csv else []
            add_specializations(conn, law_map[law_sel], specs)
            st.success("Specializations added")
        except Exception as e:
            logger.exception("add_specializations failed")
            st.error(f"{e}")

st.subheader("View Lawyer Caseload")
lawyers2 = list_lawyers(conn)
law_map2 = {f"{r['bar_number']} - {r['first_name']} {r['last_name']}": r['bar_number'] for r in lawyers2}
law_sel2 = st.selectbox("Lawyer", list(law_map2.keys()))
if st.button("Load Caseload"):
    try:
        rows = list_lawyer_caseload(conn, law_map2[law_sel2])
        st.dataframe(rows)
    except Exception as e:
        logger.exception("list_lawyer_caseload failed")
        st.error(f"{e}")
