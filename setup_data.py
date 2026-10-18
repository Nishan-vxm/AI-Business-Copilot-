"""Download the Olist Brazilian ecommerce dataset and build a local SQLite DB.

Run:
    python scripts/setup_data.py

KaggleHub may require network access. This script does not upload data to GitHub.
"""
from __future__ import annotations

import glob
import os
from pathlib import Path
import sqlite3

import kagglehub
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "olist_business.db"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    csv_files = glob.glob(os.path.join(dataset_path, "*.csv"))
    if not csv_files:
        raise RuntimeError(f"No CSV files found in downloaded dataset: {dataset_path}")

    with sqlite3.connect(DB_PATH) as conn:
        for csv_file in csv_files:
            table_name = Path(csv_file).stem
            print(f"Loading {table_name}...")
            frame = pd.read_csv(csv_file)
            frame.to_sql(table_name, conn, if_exists="replace", index=False)

    print(f"\nDatabase created: {DB_PATH}")
    print(f"Tables loaded: {len(csv_files)}")


if __name__ == "__main__":
    main()
