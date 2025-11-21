import re

ROLES = {"lawyer","paralegal","receptionist","investigator"}
CLIENT_TYPES = {"individual","business","cartel-affiliated"}
CASE_STATUSES = {"open","closed"}
ASSOCIATE_STATUSES = {"active","dead","missing"}

def validate_role(role):
    if role not in ROLES:
        raise ValueError("Invalid role")
    return role

def validate_client_type(v):
    if v not in CLIENT_TYPES:
        raise ValueError("Invalid client type")
    return v

def validate_case_status(v):
    if v not in CASE_STATUSES:
        raise ValueError("Invalid case status")
    return v

def validate_associate_status(v):
    if v not in ASSOCIATE_STATUSES:
        raise ValueError("Invalid associate status")
    return v

def validate_email(v):
    if v is None or v == "":
        return v
    if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", v):
        raise ValueError("Invalid email")
    return v

def validate_phone(v):
    if v is None:
        return v
    s = str(v)
    if not s.isdigit() or len(s) != 10:
        raise ValueError("Invalid phone")
    return int(s)

def ensure_date_str(v):
    if hasattr(v, "isoformat"):
        return v.isoformat()
    s = str(v)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        raise ValueError("Invalid date format, expected YYYY-MM-DD")
    return s

def ensure_int(v):
    try:
        return int(v)
    except Exception:
        raise ValueError("Expected integer")
