import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "heart_analysis.db"


def _where(filters: dict | None) -> tuple[str, list]:
    if not filters:
        return "", []
    clauses = []
    params = []
    mapping = {
        "gender": "Sex",
        "age_group": "[Age Group]",
        "smoking": "Smoking",
        "alcohol": "AlcoholDrinking",
    }
    for key, column in mapping.items():
        value = filters.get(key)
        if value and value != "All":
            clauses.append(f"{column} = ?")
            params.append(value)
    if not clauses:
        return "", []
    return "WHERE " + " AND ".join(clauses), params


def query_one(sql: str, params: list | None = None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(sql, params or [])
        row = cursor.fetchone()
        return row[0] if row else None


def query_all(sql: str, params: list | None = None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(sql, params or [])
        return cursor.fetchall()


def summary_metrics(filters: dict | None = None) -> dict:
    where, params = _where(filters)
    base = f"FROM heart_data {where}"

    total_patients = query_one(f"SELECT COUNT(*) {base}", params) or 0
    if where:
        heart_cases = query_one(f"SELECT COUNT(*) FROM heart_data {where} AND HeartDisease = 'Yes'", params) or 0
    else:
        heart_cases = query_one("SELECT COUNT(*) FROM heart_data WHERE HeartDisease = 'Yes'") or 0

    prevalence = round((heart_cases * 100.0 / total_patients), 2) if total_patients else 0.0

    return {
        "total_patients": total_patients,
        "heart_disease_cases": heart_cases,
        "heart_disease_prevalence": prevalence,
        "average_cholesterol": query_one(f"SELECT ROUND(AVG(CholesterolEstimate), 2) {base}", params) or 0,
        "average_age": query_one(f"SELECT ROUND(AVG(AgeMidpoint), 2) {base}", params) or 0,
    }


def gender_distribution(filters: dict | None = None):
    where, params = _where(filters)
    return query_all(f"SELECT Sex, COUNT(*) FROM heart_data {where} GROUP BY Sex ORDER BY COUNT(*) DESC", params)


def smoking_vs_heart_disease(filters: dict | None = None):
    where, params = _where(filters)
    return query_all(
        f"SELECT Smoking, HeartDisease, COUNT(*) FROM heart_data {where} GROUP BY Smoking, HeartDisease",
        params,
    )


def alcohol_vs_heart_disease(filters: dict | None = None):
    where, params = _where(filters)
    return query_all(
        f"SELECT AlcoholDrinking, HeartDisease, COUNT(*) FROM heart_data {where} GROUP BY AlcoholDrinking, HeartDisease",
        params,
    )


def distinct_filter_values() -> dict:
    return {
        "genders": [r[0] for r in query_all("SELECT DISTINCT Sex FROM heart_data ORDER BY Sex")],
        "age_groups": [r[0] for r in query_all("SELECT DISTINCT [Age Group] FROM heart_data ORDER BY [Age Group]")],
        "smoking": [r[0] for r in query_all("SELECT DISTINCT Smoking FROM heart_data ORDER BY Smoking")],
        "alcohol": [r[0] for r in query_all("SELECT DISTINCT AlcoholDrinking FROM heart_data ORDER BY AlcoholDrinking")],
    }
