"""Question-to-SQL orchestration, validation, and bounded repair retry."""
from __future__ import annotations

from src.database import DB_PATH, get_schema, safe_run_sql, validate_sql
from src.llm import generate_sql_with_llm


def business_copilot_query(question: str, max_retries: int = 1) -> dict:
    if not question or not question.strip():
        return {"sql": None, "result": None, "error": "Please enter a question."}

    schema = get_schema(DB_PATH)
    current_question = question.strip()
    last_error = None
    last_sql = None

    for attempt in range(max_retries + 1):
        try:
            sql = generate_sql_with_llm(current_question, schema)
            last_sql = sql
            valid, message = validate_sql(sql)
            if not valid:
                raise ValueError(message)

            result = safe_run_sql(sql, db_path=DB_PATH)
            return {
                "sql": sql,
                "result": result,
                "error": None,
                "attempts": attempt + 1
            }
        except Exception as exc:
            last_error = str(exc)
            if attempt < max_retries:
                current_question = (
                    f"Original business question: {question}\n"
                    f"Your previous SQL failed with this error: {last_error}\n"
                    "Generate a corrected SQLite SELECT query. "
                    "Use only the provided schema. Return SQL only."
                )

    return {
        "sql": None,
        "last_sql": last_sql,
        "result": None,
        "error": last_error,
        "attempts": max_retries + 1
    }
