from pathlib import Path

import pandas as pd

from backend.data_processing import get_processed_data

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "heart_analysis.db"


def infer_sqlite_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series):
        return "REAL"
    return "TEXT"


def initialize_database(force_rebuild: bool = False) -> Path:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if force_rebuild and DB_PATH.exists():
        DB_PATH.unlink()

    df = get_processed_data()
    dtype_map = {col: infer_sqlite_type(df[col]) for col in df.columns}

    import sqlite3

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("heart_data", conn, if_exists="replace", index=False, dtype=dtype_map)

    return DB_PATH


if __name__ == "__main__":
    path = initialize_database(force_rebuild=True)
    print(f"Database created at: {path}")
