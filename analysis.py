import pandas as pd
import plotly.express as px

from database.database_setup import DB_PATH


def filtered_df(filters: dict | None = None) -> pd.DataFrame:
    where_parts = []
    params = []
    filters = filters or {}
    mapping = {
        "gender": "Sex",
        "age_group": "[Age Group]",
        "smoking": "Smoking",
        "alcohol": "AlcoholDrinking",
    }
    for k, c in mapping.items():
        v = filters.get(k)
        if v and v != "All":
            where_parts.append(f"{c} = ?")
            params.append(v)
    where = ""
    if where_parts:
        where = "WHERE " + " AND ".join(where_parts)

    sql = f"SELECT * FROM heart_data {where}"
    import sqlite3

    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def _apply_tableau_style(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=34, r=20, t=54, b=34),
        font=dict(family="Segoe UI, Arial, sans-serif", size=12, color="#233042"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf1f7", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#edf1f7", zeroline=False)


def build_charts(filters: dict | None = None) -> dict:
    df = filtered_df(filters)

    if df.empty:
        return {}

    age_order = ["18-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]

    prevalence = df["HeartDisease"].value_counts().reset_index()
    prevalence.columns = ["HeartDisease", "Count"]
    fig_prevalence = px.pie(
        prevalence,
        names="HeartDisease",
        values="Count",
        title="Heart Disease Prevalence",
        color="HeartDisease",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
        hole=0.35,
    )

    age_risk = (
        df.groupby("Age Group")["HeartDisease"]
        .apply(lambda s: (s == "Yes").mean() * 100)
        .reindex(age_order)
        .reset_index(name="RiskPct")
        .fillna(0)
    )
    fig_age_risk = px.bar(
        age_risk,
        x="Age Group",
        y="RiskPct",
        title="Age Group vs Heart Disease Risk (%)",
        color_discrete_sequence=["#f28e2b"],
    )

    gender_risk = df.groupby(["Sex", "HeartDisease"]).size().reset_index(name="Count")
    fig_gender = px.bar(
        gender_risk,
        x="Sex",
        y="Count",
        color="HeartDisease",
        barmode="group",
        title="Gender Risk Distribution",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    heat = df.groupby(["Smoking", "AlcoholDrinking", "HeartDisease"]).size().reset_index(name="Count")
    fig_heat = px.density_heatmap(
        heat,
        x="Smoking",
        y="AlcoholDrinking",
        z="Count",
        facet_col="HeartDisease",
        title="Smoking & Alcohol Impact by Heart Disease",
        color_continuous_scale="Blues",
    )

    fig_hist = px.histogram(
        df,
        x="AgeMidpoint",
        color="HeartDisease",
        nbins=20,
        barmode="overlay",
        title="Age Distribution Histogram",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    risk_dist = df["Lifestyle Risk Score"].value_counts().sort_index().reset_index()
    risk_dist.columns = ["Lifestyle Risk Score", "Count"]
    fig_risk_dist = px.bar(
        risk_dist,
        x="Lifestyle Risk Score",
        y="Count",
        title="Lifestyle Risk Score Distribution",
        color_discrete_sequence=["#59a14f"],
    )

    smoke_hd = df.groupby(["Smoking", "HeartDisease"]).size().reset_index(name="Count")
    fig_smoke_hd = px.bar(
        smoke_hd,
        x="Smoking",
        y="Count",
        color="HeartDisease",
        barmode="group",
        title="Smoking vs Heart Disease",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    alcohol_hd = df.groupby(["AlcoholDrinking", "HeartDisease"]).size().reset_index(name="Count")
    fig_alcohol_hd = px.bar(
        alcohol_hd,
        x="AlcoholDrinking",
        y="Count",
        color="HeartDisease",
        barmode="group",
        title="Alcohol Use vs Heart Disease",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    gen_health = df.groupby(["GenHealth", "HeartDisease"]).size().reset_index(name="Count")
    health_order = ["Excellent", "Very good", "Good", "Fair", "Poor", "Unknown"]
    gen_health["GenHealth"] = pd.Categorical(gen_health["GenHealth"], categories=health_order, ordered=True)
    fig_health = px.bar(
        gen_health.sort_values("GenHealth"),
        x="GenHealth",
        y="Count",
        color="HeartDisease",
        barmode="stack",
        title="General Health vs Heart Disease",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    fig_bmi = px.box(
        df,
        x="HeartDisease",
        y="BMI",
        color="HeartDisease",
        title="BMI Distribution by Heart Disease",
        color_discrete_map={"Yes": "#e15759", "No": "#4e79a7"},
    )

    figures = {
        "prevalence": fig_prevalence,
        "age_risk": fig_age_risk,
        "gender_risk": fig_gender,
        "lifestyle_heatmap": fig_heat,
        "age_histogram": fig_hist,
        "risk_distribution": fig_risk_dist,
        "smoking_vs_hd": fig_smoke_hd,
        "alcohol_vs_hd": fig_alcohol_hd,
        "gen_health_vs_hd": fig_health,
        "bmi_by_hd": fig_bmi,
    }

    for fig in figures.values():
        _apply_tableau_style(fig)

    return {k: v.to_json() for k, v in figures.items()}
