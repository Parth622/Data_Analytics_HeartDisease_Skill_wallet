import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATHS = [
    ROOT / "data" / "Heart_new2.csv",
    ROOT / "Heart_new2.csv",
]


def _find_dataset_path() -> Path:
    for path in DEFAULT_DATA_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("Heart_new2.csv not found in project root or data directory")


def load_raw_data(path: Path | None = None) -> pd.DataFrame:
    source = path or _find_dataset_path()
    return pd.read_csv(source)


def _age_to_group(age_value: str) -> str:
    if not isinstance(age_value, str):
        return "Unknown"
    if age_value == "80 or older":
        return "80+"
    match = re.match(r"(\d+)-", age_value)
    if not match:
        return "Unknown"
    age = int(match.group(1))
    if age < 30:
        return "18-29"
    if age < 40:
        return "30-39"
    if age < 50:
        return "40-49"
    if age < 60:
        return "50-59"
    if age < 70:
        return "60-69"
    if age < 80:
        return "70-79"
    return "80+"


def _age_to_midpoint(age_value: str) -> int:
    if not isinstance(age_value, str):
        return 0
    if age_value == "80 or older":
        return 82
    match = re.match(r"(\d+)-(\d+)", age_value)
    if not match:
        return 0
    low, high = int(match.group(1)), int(match.group(2))
    return int((low + high) / 2)


def _cholesterol_category(chol: float) -> str:
    if chol < 180:
        return "Desirable"
    if chol < 220:
        return "Borderline"
    return "High"


def _bp_category(row: pd.Series) -> str:
    score = row["BMI"] + (row["AgeMidpoint"] / 8.0)
    if score < 25:
        return "Normal"
    if score < 30:
        return "Elevated"
    if score < 36:
        return "High Stage 1"
    return "High Stage 2"


def _lifestyle_score(row: pd.Series) -> int:
    score = 0
    score += 2 if row.get("Smoking") == "Yes" else 0
    score += 1 if row.get("AlcoholDrinking") == "Yes" else 0
    score += 2 if row.get("PhysicalActivity") == "No" else 0
    score += 1 if row.get("SleepTime", 0) < 6 or row.get("SleepTime", 0) > 9 else 0
    score += 2 if row.get("Diabetic") in {"Yes", "Yes (during pregnancy)"} else 0
    score += 2 if row.get("Stroke") == "Yes" else 0
    return score


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()

    for col in ["BMI", "PhysicalHealth", "MentalHealth", "SleepTime"]:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    cleaned = cleaned.replace({"": np.nan, "Unknown": np.nan})

    for col in cleaned.columns:
        series = cleaned[col]
        if pd.api.types.is_numeric_dtype(series):
            cleaned[col] = series.fillna(series.median())
        else:
            cleaned[col] = series.astype("string").fillna("Unknown")

    cleaned["AgeMidpoint"] = cleaned["AgeCategory"].apply(_age_to_midpoint)
    cleaned["Age Group"] = cleaned["AgeCategory"].apply(_age_to_group)

    # Proxy feature used because source dataset does not provide direct cholesterol readings.
    cleaned["CholesterolEstimate"] = (cleaned["BMI"] * 7.2 + cleaned["AgeMidpoint"] * 0.9).clip(120, 320)
    cleaned["Cholesterol Category"] = cleaned["CholesterolEstimate"].apply(_cholesterol_category)

    cleaned["Blood Pressure Category"] = cleaned.apply(_bp_category, axis=1)
    cleaned["Lifestyle Risk Score"] = cleaned.apply(_lifestyle_score, axis=1)

    return cleaned


def get_processed_data(path: Path | None = None) -> pd.DataFrame:
    raw = load_raw_data(path)
    return process_data(raw)
