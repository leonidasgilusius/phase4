import logging
import os
import streamlit as st

def get_db_settings():
    try:
        s = dict(st.secrets)  # may raise if no secrets.toml; handled below
    except Exception:
        s = {}
    host = s.get("mysql_host", os.getenv("MYSQL_HOST", "localhost"))
    user = s.get("mysql_user", os.getenv("MYSQL_USER", "root"))
    password = s.get("mysql_password", os.getenv("MYSQL_PASSWORD", ""))
    database = s.get("mysql_database", os.getenv("MYSQL_DATABASE", "ItsAllGoodMan"))
    port = int(s.get("mysql_port", os.getenv("MYSQL_PORT", "3306")))
    return {"host": host, "user": user, "password": password, "database": database, "port": port}

def configure_logging():
    try:
        level_name = st.secrets.get("log_level")
    except Exception:
        level_name = os.getenv("LOG_LEVEL", "INFO")
    level = getattr(logging, (level_name or "INFO").upper(), logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    else:
        root.setLevel(level)
    return level
