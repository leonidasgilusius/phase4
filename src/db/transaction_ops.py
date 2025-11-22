import logging
from typing import Iterable
from services.validation import validate_role, validate_client_type, validate_case_status, validate_associate_status, validate_email, validate_phone, ensure_date_str, ensure_int

logger = logging.getLogger(__name__)

def _quote_ident(name: str) -> str:
    return f"`{name}`"

def _next_id(conn, table: str, id_col: str) -> int:
    t = _quote_ident(table) if table.lower() == "transaction" else table
    c = id_col
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(MAX({c}),0)+1 AS next_id FROM {t}")
        nid = cur.fetchone()["next_id"] or 1
        while True:
            cur.execute(f"SELECT 1 FROM {t} WHERE {c}=%s", (nid,))
            if not cur.fetchone():
                break
            nid += 1
    return int(nid)

def create_employee(conn, first_name, last_name, role, salary, trust_level):
    role = validate_role(role)
    salary = ensure_int(salary)
    trust_level = ensure_int(trust_level)
    try:
        with conn.cursor() as cur:
            new_id = _next_id(conn, "Employee", "employee_id")
            sql = "INSERT INTO Employee (employee_id, first_name, last_name, role, salary, trust_level) VALUES (%s,%s,%s,%s,%s,%s)"
            params = (new_id, first_name, last_name, role, salary, trust_level)
            logger.debug("create_employee %s", params)
            cur.execute(sql, params)
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise

def upgrade_to_lawyer(conn, employee_id, bar_number):
    employee_id = ensure_int(employee_id)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM Employee WHERE employee_id=%s", (employee_id,))
            if not cur.fetchone():
                raise ValueError("Employee not found")
            # Prevent duplicate promotion
            cur.execute("SELECT 1 FROM Lawyer WHERE lawyer_id=%s", (employee_id,))
            if cur.fetchone():
                raise ValueError("Employee is already a lawyer")
            # Determine bar number
            if bar_number in (None, ""):
                assigned_bar = _next_id(conn, "Lawyer", "bar_number")
            else:
                assigned_bar = ensure_int(bar_number)
            sql = "INSERT INTO Lawyer (lawyer_id, bar_number) VALUES (%s,%s)"
            params = (employee_id, assigned_bar)
            logger.debug("upgrade_to_lawyer %s", params)
            cur.execute(sql, params)
        conn.commit()
        return assigned_bar
    except Exception:
        conn.rollback()
        raise

def add_specializations(conn, bar_number, specializations: Iterable[str]):
    bar_number = ensure_int(bar_number)
    specs = [s.strip() for s in specializations if s and s.strip()]
    if not specs:
        return
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO Specialization_table (specialization, lawyer) VALUES (%s,%s)"
            data = [(s, bar_number) for s in specs]
            logger.debug("add_specializations %s", data)
            cur.executemany(sql, data)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def create_client(conn, first_name, last_name, phone, email, address, type_value, date_joined, account_no, lawyer_assigned):
    phone = validate_phone(phone)
    email = validate_email(email)
    type_value = validate_client_type(type_value)
    date_joined = ensure_date_str(date_joined)
    account_no = ensure_int(account_no) if account_no not in (None, "") else None
    lawyer_assigned = ensure_int(lawyer_assigned) if lawyer_assigned not in (None, "") else None
    try:
        with conn.cursor() as cur:
            new_id = _next_id(conn, "Client", "client_id")
            sql = """INSERT INTO Client (client_id, first_name, last_name, phone, email, address, type, date_joined, account_no, lawyer_assigned)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            params = (new_id, first_name, last_name, phone, email, address, type_value, date_joined, account_no, lawyer_assigned)
            logger.debug("create_client %s", params)
            cur.execute(sql, params)
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise

def reassign_client_lawyer(conn, client_id, new_bar_number):
    client_id = ensure_int(client_id)
    new_bar_number = ensure_int(new_bar_number)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM Lawyer WHERE bar_number=%s", (new_bar_number,))
            if not cur.fetchone():
                raise ValueError("Lawyer not found")
            sql = "UPDATE Client SET lawyer_assigned=%s WHERE client_id=%s"
            params = (new_bar_number, client_id)
            logger.debug("reassign_client_lawyer %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def create_case(conn, case_title, client_id, description, status):
    status = validate_case_status(status)
    client_id = ensure_int(client_id)
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO Cases (case_title, client_id, description, status) VALUES (%s,%s,%s,%s)"
            params = (case_title, client_id, description, status)
            logger.debug("create_case %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def update_case_status(conn, case_title, status):
    status = validate_case_status(status)
    try:
        with conn.cursor() as cur:
            sql = "UPDATE Cases SET status=%s WHERE case_title=%s"
            params = (status, case_title)
            logger.debug("update_case_status %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def schedule_trial(conn, case_title, trial_date):
    trial_date = ensure_date_str(trial_date)
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO Trial (trial_date, case_title) VALUES (%s,%s)"
            params = (trial_date, case_title)
            logger.debug("schedule_trial %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def add_required_document(conn, case_title, trial_date, document_id):
    trial_date = ensure_date_str(trial_date)
    document_id = ensure_int(document_id)
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO Documents_required (document_id, trial_date, case_title) VALUES (%s,%s,%s)"
            params = (document_id, trial_date, case_title)
            logger.debug("add_required_document %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def record_fee_payment(conn, source_account, destination_account, amount, date_value, client_id, case_title):
    source_account = ensure_int(source_account)
    destination_account = ensure_int(destination_account)
    amount = ensure_int(amount)
    date_value = ensure_date_str(date_value)
    client_id = ensure_int(client_id)
    try:
        with conn.cursor() as cur:
            # Ensure the case belongs to the client
            cur.execute("SELECT 1 FROM Cases WHERE case_title=%s AND client_id=%s", (case_title, client_id))
            if not cur.fetchone():
                raise ValueError("Client is not associated with the selected case")
            transaction_id = _next_id(conn, "Transaction", "transaction_id")
            sql1 = "INSERT INTO `Transaction` (transaction_id, source_account, destination_account, amount, date) VALUES (%s,%s,%s,%s,%s)"
            p1 = (transaction_id, source_account, destination_account, amount, date_value)
            logger.debug("record_fee_payment.transaction %s", p1)
            cur.execute(sql1, p1)
            sql2 = "INSERT INTO Fee_payment (transaction_id, client_id, case_title) VALUES (%s,%s,%s)"
            p2 = (transaction_id, client_id, case_title)
            logger.debug("record_fee_payment.fee %s", p2)
            cur.execute(sql2, p2)
        conn.commit()
        return transaction_id
    except Exception:
        conn.rollback()
        raise

def record_business_fee(conn, source_account, destination_account, amount, date_value, business_name, location):
    source_account = ensure_int(source_account)
    destination_account = ensure_int(destination_account)
    amount = ensure_int(amount)
    date_value = ensure_date_str(date_value)
    try:
        with conn.cursor() as cur:
            # Ensure business exists
            cur.execute(
                "SELECT 1 FROM Associated_business WHERE business_name=%s AND location=%s",
                (business_name, location),
            )
            if not cur.fetchone():
                raise ValueError("Selected business does not exist")
            transaction_id = _next_id(conn, "Transaction", "transaction_id")
            sql1 = "INSERT INTO `Transaction` (transaction_id, source_account, destination_account, amount, date) VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql1, (transaction_id, source_account, destination_account, amount, date_value))
            sql2 = "INSERT INTO Business_fee (transaction_id, business_name, location) VALUES (%s,%s,%s)"
            cur.execute(sql2, (transaction_id, business_name, location))
        conn.commit()
        return transaction_id
    except Exception:
        conn.rollback()
        raise

def create_associate(conn, name, status, loyalty_score, account_no, alias_client_id):
    status = validate_associate_status(status)
    loyalty_score = ensure_int(loyalty_score)
    account_no = ensure_int(account_no) if account_no not in (None, "") else None
    alias_client_id = ensure_int(alias_client_id) if alias_client_id not in (None, "") else None
    try:
        with conn.cursor() as cur:
            new_id = _next_id(conn, "Associate", "associate_id")
            sql = "INSERT INTO Associate (associate_id, name, status, loyalty_score, account_no, alias) VALUES (%s,%s,%s,%s,%s,%s)"
            params = (new_id, name, status, loyalty_score, account_no, alias_client_id)
            logger.debug("create_associate %s", params)
            cur.execute(sql, params)
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise

def mark_criminal_associate(conn, associate_id, codename):
    associate_id = ensure_int(associate_id)
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO CriminalAssociate (associate_id, codename) VALUES (%s,%s)"
            params = (associate_id, codename)
            logger.debug("mark_criminal_associate %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def add_skill(conn, associate_id, skill_name):
    associate_id = ensure_int(associate_id)
    try:
        with conn.cursor() as cur:
            sql = "INSERT INTO Skills (skill_name, associate_id) VALUES (%s,%s)"
            params = (skill_name, associate_id)
            logger.debug("add_skill %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def create_document(conn, title, type_value, file_path, file_size_bytes, mime_type, create_date):
    file_size_bytes = ensure_int(file_size_bytes)
    create_date = ensure_date_str(create_date)
    try:
        with conn.cursor() as cur:
            document_id = _next_id(conn, "Document", "document_id")
            sql = (
                "INSERT INTO Document (document_id, title, type, file_path, file_size_bytes, mime_type, create_date) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)"
            )
            params = (document_id, title, type_value, file_path, file_size_bytes, mime_type, create_date)
            logger.debug("create_document %s", params)
            cur.execute(sql, params)
        conn.commit()
        return document_id
    except Exception:
        conn.rollback()
        raise

def attach_document_to_casefile(conn, case_title, trial_date, document_id, client_id):
    trial_date = ensure_date_str(trial_date)
    document_id = ensure_int(document_id)
    client_id = ensure_int(client_id)
    try:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO Casefile (trial_date, document_id, case_title, client_id) "
                "VALUES (%s,%s,%s,%s)"
            )
            params = (trial_date, document_id, case_title, client_id)
            logger.debug("attach_document_to_casefile %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def remove_document_from_casefile(conn, case_title, trial_date, document_id, client_id):
    trial_date = ensure_date_str(trial_date)
    document_id = ensure_int(document_id)
    client_id = ensure_int(client_id)
    try:
        with conn.cursor() as cur:
            sql = (
                "DELETE FROM Casefile WHERE trial_date=%s AND document_id=%s AND case_title=%s AND client_id=%s"
            )
            params = (trial_date, document_id, case_title, client_id)
            logger.debug("remove_document_from_casefile %s", params)
            cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
