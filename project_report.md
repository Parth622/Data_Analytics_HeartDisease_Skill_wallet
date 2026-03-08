# Heart Disease Analytics Platform

## Overview
A Flask + SQLite analytics portal that simulates a Tableau-style BI experience for `Heart_new2.csv`.

## Components
- Data ingestion and cleaning with Pandas/NumPy
- SQLite analytical storage (`heart_data`)
- SQL analysis service layer
- Plotly interactive visualizations
- Dashboard, Story, Performance, and Documentation web pages

## Data Preparation
1. Remove duplicates
2. Handle missing values
3. Coerce numeric types
4. Create calculated fields:
   - `Age Group`
   - `Cholesterol Category` (from `CholesterolEstimate` proxy)
   - `Blood Pressure Category`
   - `Lifestyle Risk Score`

## Run
```bash
python -m pip install flask pandas numpy plotly
python -m backend.app
```

## Notes
The source file does not include direct cholesterol or blood pressure values. The app uses transparent proxy features for BI demonstrations.

