import logging

logger = logging.getLogger(__name__)

def run_sql_script(conn, sql_text: str):
    """Execute a SQL script containing multiple statements separated by semicolons.
    This is a simple splitter suitable for our schema/populate files.
    """
    # Remove Windows newlines and split by semicolons
    text = sql_text.replace("\r", "\n")
    # Strip line comments
    lines = []
    for line in text.split("\n"):
        l = line.strip()
        if not l or l.startswith("--"):
            continue
        lines.append(line)
    normalized = "\n".join(lines)
    statements = [s.strip() for s in normalized.split(";") if s.strip()]
    with conn.cursor() as cur:
        for stmt in statements:
            logger.debug("Executing statement: %s", stmt[:200])
            cur.execute(stmt)
    conn.commit()
