import logging
import streamlit as st

logger = logging.getLogger(__name__)

def _ui_debug(sql, params):
    try:
        if st.session_state.get("debug"):
            st.caption(f"SQL: {sql}")
            st.caption(f"Params: {params}")
    except Exception:
        pass

def get_kpis(conn, upcoming_days=7):
    with conn.cursor() as cur:
        sql1 = "SELECT COUNT(*) AS open_cases FROM Cases WHERE status = %s"
        cur.execute(sql1, ("open",))
        _ui_debug(sql1, ("open",))
        open_cases = cur.fetchone()["open_cases"]

        sql2 = "SELECT COUNT(*) AS upcoming_trials FROM Trial WHERE trial_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)"
        cur.execute(sql2, (upcoming_days,))
        _ui_debug(sql2, (upcoming_days,))
        upcoming_trials = cur.fetchone()["upcoming_trials"]

        sql3 = """SELECT COALESCE(SUM(t.amount),0) AS total_mtd
                  FROM `Transaction` t
                  JOIN Fee_payment f ON f.transaction_id = t.transaction_id
                  WHERE t.date BETWEEN DATE_FORMAT(CURDATE(), '%Y-%m-01') AND CURDATE()"""
        cur.execute(sql3)
        _ui_debug(sql3, None)
        total_mtd = cur.fetchone()["total_mtd"]

        sql4 = """SELECT s.specialization, COUNT(ca.case_title) AS open_count
                  FROM Specialization_table s
                  JOIN Lawyer l ON s.lawyer = l.bar_number
                  LEFT JOIN Client c ON c.lawyer_assigned = l.bar_number
                  LEFT JOIN Cases ca ON ca.client_id = c.client_id AND ca.status = %s
                  GROUP BY s.specialization
                  ORDER BY open_count DESC
                  LIMIT 5"""
        cur.execute(sql4, ("open",))
        _ui_debug(sql4, ("open",))
        top_specs = cur.fetchall()
        return {"open_cases": open_cases, "upcoming_trials": upcoming_trials, "total_fees_mtd": total_mtd, "top_specializations": top_specs}

def search_clients(conn, q, type_filter=None, lawyer=None, limit=50):
    like = f"%{q.strip()}%" if q else "%"
    sql = "SELECT client_id, first_name, last_name, email, phone, type, date_joined, lawyer_assigned FROM Client WHERE (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
    params = [like, like, like]
    if type_filter:
        sql += " AND type = %s"
        params.append(type_filter)
    if lawyer:
        sql += " AND lawyer_assigned = %s"
        params.append(lawyer)
    sql += " ORDER BY date_joined DESC LIMIT %s"
    params.append(int(limit))
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        _ui_debug(sql, tuple(params))
        return cur.fetchall()

def get_case_summary(conn, case_title):
    with conn.cursor() as cur:
        sql1 = (
            "SELECT ca.case_title, ca.description, ca.status, "
            "c.client_id, c.first_name AS client_first, c.last_name AS client_last, c.lawyer_assigned, "
            "le.first_name AS lawyer_first, le.last_name AS lawyer_last "
            "FROM Cases ca LEFT JOIN Client c ON c.client_id = ca.client_id "
            "LEFT JOIN Lawyer l ON l.bar_number = c.lawyer_assigned "
            "LEFT JOIN Employee le ON le.employee_id = l.lawyer_id "
            "WHERE ca.case_title = %s"
        )
        cur.execute(sql1, (case_title,))
        _ui_debug(sql1, (case_title,))
        case_row = cur.fetchone()

        sql2 = "SELECT MAX(trial_date) AS latest_trial FROM Trial WHERE case_title = %s"
        cur.execute(sql2, (case_title,))
        _ui_debug(sql2, (case_title,))
        latest_trial = cur.fetchone()["latest_trial"]

        sql3 = """SELECT COALESCE(SUM(t.amount),0) AS total_paid
                  FROM Fee_payment f JOIN `Transaction` t ON t.transaction_id = f.transaction_id
                  WHERE f.case_title = %s"""
        cur.execute(sql3, (case_title,))
        _ui_debug(sql3, (case_title,))
        total_paid = cur.fetchone()["total_paid"]

        return {"case": case_row, "latest_trial": latest_trial, "total_paid": total_paid,}

def get_upcoming_trials_with_missing_docs(conn, days=14):
    sql = """SELECT tr.trial_date, tr.case_title,
                    SUM(CASE WHEN cf.document_id IS NULL THEN 1 ELSE 0 END) AS missing_docs
             FROM Trial tr
             LEFT JOIN Documents_required dr ON dr.trial_date = tr.trial_date AND dr.case_title = tr.case_title
             LEFT JOIN Casefile cf ON cf.trial_date = dr.trial_date AND cf.case_title = dr.case_title AND cf.document_id = dr.document_id
             WHERE tr.trial_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
             GROUP BY tr.trial_date, tr.case_title
             HAVING missing_docs > 0
             ORDER BY tr.trial_date ASC"""
    with conn.cursor() as cur:
        cur.execute(sql, (days,))
        _ui_debug(sql, (days,))
        return cur.fetchall()

def list_lawyer_caseload(conn, bar_number):
    sql = (
        "SELECT ca.case_title, ca.status, c.client_id, c.first_name, c.last_name "
        "FROM Client c JOIN Cases ca ON ca.client_id = c.client_id "
        "WHERE c.lawyer_assigned = %s ORDER BY (ca.status='open') DESC, ca.case_title"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (bar_number,))
        _ui_debug(sql, (bar_number,))
        return cur.fetchall()

def document_search(conn, title_like=None, type_filter=None, date_from=None, date_to=None, mime=None, limit=100):
    sql = "SELECT document_id, title, type, file_path, file_size_bytes, mime_type, created_date FROM Document WHERE 1=1"
    params = []
    if title_like:
        sql += " AND title LIKE %s"
        params.append(f"%{title_like}%")
    if type_filter:
        sql += " AND type = %s"
        params.append(type_filter)
    if date_from:
        sql += " AND created_date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND created_date <= %s"
        params.append(date_to)
    if mime:
        sql += " AND mime_type = %s"
        params.append(mime)
    sql += " ORDER BY created_date DESC LIMIT %s"
    params.append(int(limit))
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        _ui_debug(sql, tuple(params))
        return cur.fetchall()

def payments_ledger(conn, client_id=None, case_title=None, date_from=None, date_to=None):
    sql = (
        "SELECT t.transaction_id, t.amount, t.date, f.client_id, f.case_title "
        "FROM Fee_payment f JOIN `Transaction` t ON t.transaction_id = f.transaction_id WHERE 1=1"
    )
    params = []
    if client_id:
        sql += " AND f.client_id = %s"
        params.append(client_id)
    if case_title:
        sql += " AND f.case_title = %s"
        params.append(case_title)
    if date_from:
        sql += " AND t.date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND t.date <= %s"
        params.append(date_to)
    sql += " ORDER BY t.date DESC, t.transaction_id DESC"
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        _ui_debug(sql, tuple(params))
        rows = cur.fetchall()
        total = sum(r.get("amount", 0) for r in rows)
        return {"rows": rows, "total": total}

def find_associates(conn, status=None, loyalty_min=None, loyalty_max=None):
    sql = (
        "SELECT a.associate_id, a.name, a.status, a.loyalty_score, a.account_no, a.alias, "
        "CONCAT(c.first_name, ' ', c.last_name) AS alias_name "
        "FROM Associate a LEFT JOIN Client c ON c.client_id = a.alias WHERE 1=1"
    )
    params = []
    if status:
        sql += " AND a.status = %s"
        params.append(status)
    if loyalty_min is not None:
        sql += " AND a.loyalty_score >= %s"
        params.append(int(loyalty_min))
    if loyalty_max is not None:
        sql += " AND a.loyalty_score <= %s"
        params.append(int(loyalty_max))
    sql += " ORDER BY a.loyalty_score DESC, a.name"
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        _ui_debug(sql, tuple(params))
        return cur.fetchall()

def find_criminal_associates_by_skills(conn, skills, require_all=False):
    skills = [s for s in (skills or []) if s]
    if not skills:
        return []
    placeholders = ",".join(["%s"] * len(skills))
    sql = (
        "SELECT a.associate_id, a.name, a.status, a.loyalty_score, GROUP_CONCAT(DISTINCT s.skill_name) AS skills "
        "FROM CriminalAssociate ca JOIN Associate a ON a.associate_id = ca.associate_id "
        f"JOIN Skills s ON s.associate_id = ca.associate_id WHERE s.skill_name IN ({placeholders}) "
        "GROUP BY a.associate_id, a.name, a.status, a.loyalty_score "
        + ("HAVING COUNT(DISTINCT s.skill_name) = %s" if require_all else "HAVING COUNT(DISTINCT s.skill_name) >= 1")
    )
    params = list(skills)
    if require_all:
        params.append(len(skills))
    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        _ui_debug(sql, tuple(params))
        return cur.fetchall()

def list_trials_for_case(conn, case_title):
    sql = "SELECT trial_date FROM Trial WHERE case_title = %s ORDER BY trial_date"
    with conn.cursor() as cur:
        cur.execute(sql, (case_title,))
        _ui_debug(sql, (case_title,))
        return cur.fetchall()

def list_required_docs_for_trial(conn, case_title, trial_date):
    sql = (
        "SELECT dr.document_id, d.title, d.type, d.mime_type, d.created_date "
        "FROM Documents_required dr JOIN Document d ON d.document_id = dr.document_id "
        "WHERE dr.case_title = %s AND dr.trial_date = %s"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (case_title, trial_date))
        _ui_debug(sql, (case_title, trial_date))
        return cur.fetchall()

def list_casefile_docs(conn, case_title, trial_date, client_id):
    sql = (
        "SELECT cf.document_id, d.title, d.type, d.mime_type, d.created_date "
        "FROM Casefile cf JOIN Document d ON d.document_id = cf.document_id "
        "WHERE cf.case_title = %s AND cf.trial_date = %s AND cf.client_id = %s"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (case_title, trial_date, client_id))
        _ui_debug(sql, (case_title, trial_date, client_id))
        return cur.fetchall()

def list_lawyers(conn):
    sql = (
        "SELECT l.bar_number, e.first_name, e.last_name "
        "FROM Lawyer l JOIN Employee e ON e.employee_id = l.lawyer_id "
        "ORDER BY e.first_name, e.last_name"
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return cur.fetchall()

def list_clients_basic(conn, limit=500):
    sql = "SELECT client_id, first_name, last_name FROM Client ORDER BY first_name, last_name LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(limit),))
        _ui_debug(sql, (int(limit),))
        return cur.fetchall()
    
def list_client_of_case(conn, case_title):
    sql = "SELECT client_id, first_name, last_name FROM Client natural join Cases where case_title=%s"
    with conn.cursor() as cur:
        cur.execute(sql, (str(case_title),))
        _ui_debug(sql, (str(case_title),))
        return cur.fetchone()

def list_cases_basic(conn, limit=1000):
    sql = "SELECT case_title FROM Cases ORDER BY case_title LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(limit),))
        _ui_debug(sql, (int(limit),))
        return [row["case_title"] for row in cur.fetchall()]

def list_cases_for_client(conn, client_id, limit=1000):
    sql = "SELECT case_title FROM Cases WHERE client_id = %s ORDER BY case_title LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(client_id), int(limit)))
        _ui_debug(sql, (int(client_id), int(limit)))
        return [row["case_title"] for row in cur.fetchall()]

def list_document_types(conn):
    sql = "SELECT DISTINCT type FROM Document WHERE type IS NOT NULL ORDER BY type"
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return [row["type"] for row in cur.fetchall()]

def list_mime_types(conn):
    sql = "SELECT DISTINCT mime_type FROM Document WHERE mime_type IS NOT NULL ORDER BY mime_type"
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return [row["mime_type"] for row in cur.fetchall()]

def get_upcoming_trials(conn, days=14):
    sql = (
        "SELECT trial_date, case_title FROM Trial "
        "WHERE trial_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY) "
        "ORDER BY trial_date ASC"
    )
    with conn.cursor() as cur:
        cur.execute(sql, (days,))
        _ui_debug(sql, (days,))
        return cur.fetchall()

def list_documents_basic(conn, limit=1000):
    sql = "SELECT document_id, title FROM Document ORDER BY created_date DESC LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(limit),))
        _ui_debug(sql, (int(limit),))
        return cur.fetchall()

def list_employees_basic(conn, limit=1000):
    sql = "SELECT employee_id, first_name, last_name FROM Employee ORDER BY first_name, last_name LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(limit),))
        _ui_debug(sql, (int(limit),))
        return cur.fetchall()

def list_associates_basic(conn, limit=1000):
    sql = "SELECT associate_id, name FROM Associate ORDER BY name LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(sql, (int(limit),))
        _ui_debug(sql, (int(limit),))
        return cur.fetchall()

def list_distinct_skills(conn):
    sql = "SELECT DISTINCT skill_name FROM Skills ORDER BY skill_name"
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return [row["skill_name"] for row in cur.fetchall()]

def list_all_skills(conn):
    sql = (
        "SELECT s.skill_name, s.associate_id, a.name "
        "FROM Skills s JOIN Associate a ON a.associate_id = s.associate_id "
        "ORDER BY s.skill_name, a.name"
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return cur.fetchall()

def list_criminal_associates(conn):
    sql = (
        "SELECT ca.associate_id, a.name, ca.codename "
        "FROM CriminalAssociate ca JOIN Associate a ON a.associate_id = ca.associate_id "
        "ORDER BY a.name"
    )
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return cur.fetchall()

def list_businesses(conn):
    sql = "SELECT business_name, location FROM Associated_business ORDER BY business_name, location"
    with conn.cursor() as cur:
        cur.execute(sql)
        _ui_debug(sql, None)
        return cur.fetchall()
