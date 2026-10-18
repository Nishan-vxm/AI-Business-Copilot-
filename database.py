"""SQLite dataset setup and read-only query execution."""
from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Iterable

import pandas as pd

DB_PATH = os.getenv("COPILOT_DB_PATH", "data/olist_business.db")

APPROVED_TABLES = {
    "olist_orders_dataset",
    "olist_customers_dataset",
    "olist_order_items_dataset",
    "olist_products_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_sellers_dataset",
    "olist_geolocation_dataset",
    "product_category_name_translation",
}


def get_schema(db_path: str = DB_PATH) -> dict:
    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. Run scripts/setup_data.py first."
        )
    conn = sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro", uri=True)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        schema = {}
        for (table_name,) in tables:
            cols = conn.execute(f'PRAGMA table_info("{table_name}")').fetchall()
            schema[table_name] = [
                {"column": col[1], "type": col[2]} for col in cols
            ]
        return schema
    finally:
        conn.close()


def validate_sql(query: str) -> tuple[bool, str]:
    """Basic query gate. This is defense-in-depth, not a complete SQL parser."""
    if not isinstance(query, str) or not query.strip():
        return False, "Empty query"

    q = query.strip()
    if not q.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    cleaned = q.rstrip().rstrip(";")
    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed"

    forbidden = (
        r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|"
        r"REPLACE|PRAGMA|VACUUM|REINDEX|TRIGGER)\b"
    )
    import re
    if re.search(forbidden, q, re.IGNORECASE):
        return False, "Forbidden SQL keyword detected"

    return True, "Query passed basic checks"


def safe_run_sql(
    query: str,
    max_rows: int = 1000,
    timeout_ms: int = 3000,
    db_path: str = DB_PATH,
) -> pd.DataFrame:
    valid, message = validate_sql(query)
    if not valid:
        raise ValueError(f"Query rejected: {message}")

    path = Path(db_path).resolve()
    if not path.exists():
        raise FileNotFoundError(
            f"Database not found at {path}. Run scripts/setup_data.py first."
        )

    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=3)
    start_time = time.perf_counter()

    def authorize(action, arg1, arg2, db_name, trigger):
        if action == sqlite3.SQLITE_READ:
            if arg1 and arg1 not in APPROVED_TABLES:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION}
        if hasattr(sqlite3, "SQLITE_RECURSIVE"):
            allowed.add(sqlite3.SQLITE_RECURSIVE)
        return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

    try:
        conn.execute("PRAGMA query_only = ON")
        conn.set_authorizer(authorize)

        def should_abort():
            return int((time.perf_counter() - start_time) > timeout_ms / 1000)

        conn.set_progress_handler(should_abort, 1000)
        cursor = conn.execute(query)
        if cursor.description is None:
            raise ValueError("Query must return results.")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchmany(max_rows)
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()
