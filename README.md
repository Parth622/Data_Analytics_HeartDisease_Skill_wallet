# Data_Analytics_HeartDisease_Skill_wallet
**Heart Disease Analytics Platform (Tableau-Style BI Web App)**

This project is a full-stack, interactive analytics platform built to explore heart disease risk patterns from `Heart_new2.csv`. It is designed to resemble a professional Tableau-style BI portal while being implemented entirely using Python, Flask, SQLite, Pandas, NumPy, Plotly, HTML, CSS, and Bootstrap.

The system follows a complete data analytics pipeline:
- Ingests raw CSV data
- Cleans and transforms records (duplicates, missing values, data types)
- Creates calculated analytical fields (`Age Group`, `Cholesterol Category`, `Blood Pressure Category`, `Lifestyle Risk Score`)
- Stores processed data in SQLite (`heart_data` table)
- Runs SQL-driven summary and comparative analysis
- Serves insights through interactive web dashboards and story pages

Key capabilities include:
- KPI cards (total patients, heart disease cases, average age, average cholesterol estimate)
- Dynamic filter sidebar (gender, age group, smoking, alcohol)
- 10 interactive charts with hover, zoom, and responsive behavior
- Tableau-style dashboard layout with worksheet-like visual sections
- Storytelling page for narrative insights
- Performance page with dataset size, number of visualizations, calculated fields, and SQL query timing
- Documentation page explaining objective, methodology, analysis, and future scope

The platform is modular, reproducible, and presentation-ready, demonstrating practical skills in data engineering, BI dashboard design, SQL analytics, and full-stack web integration.
