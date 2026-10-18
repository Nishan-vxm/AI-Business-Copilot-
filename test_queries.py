"""Lightweight tests for the SQL safety gate (no model download needed)."""
from src.database import validate_sql


def test_select_is_allowed():
    assert validate_sql("SELECT COUNT(*) FROM olist_orders_dataset")[0] is True


def test_update_is_rejected():
    assert validate_sql("UPDATE olist_orders_dataset SET order_status='x'")[0] is False


def test_multiple_statements_are_rejected():
    assert validate_sql("SELECT 1; SELECT 2")[0] is False


def test_empty_query_is_rejected():
    assert validate_sql("")[0] is False
