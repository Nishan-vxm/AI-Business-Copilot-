"""Qwen model loading and natural-language-to-SQL generation."""
from __future__ import annotations

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = os.getenv("COPILOT_MODEL", "Qwen/Qwen2.5-3B-Instruct")

_tokenizer = None
_model = None


def load_model():
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    _model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=dtype,
        device_map="auto"
    )
    return _tokenizer, _model


def generate_sql_with_llm(question: str, schema: dict) -> str:
    tokenizer, model = load_model()
    schema_text = "\n".join(
        f"{table}: " + ", ".join(c["column"] for c in columns)
        for table, columns in schema.items()
    )
    messages = [
        {
            "role": "system",
            "content": f"""
You generate SQLite SQL for a read-only ecommerce analytics assistant.

DATABASE SCHEMA:
{schema_text}

RULES:
1. Return exactly one SELECT query, SQL only.
2. Use only tables and columns listed in the schema.
3. Never invent a column name.
4. Use SQLite syntax, not MySQL or SQL Server syntax.
5. Never use YEAR(), MONTH(), or DATEPART().
6. For year filtering, use strftime('%Y', date_column) = '2018'.
7. Use JOINs when the question requires data from multiple tables.
8. For customer counts by state, use olist_customers_dataset and customer_state.
9. For seller counts by state, use olist_sellers_dataset and seller_state.
10. For delivered orders, filter order_status = 'delivered'.
11. Do not include markdown fences or explanations.
""".strip()
        },
        {"role": "user", "content": question}
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=220,
            do_sample=False
        )
    generated = output[0][inputs["input_ids"].shape[1]:]
    sql = tokenizer.decode(generated, skip_special_tokens=True).strip()
    return sql.replace("```sql", "").replace("```", "").strip()
