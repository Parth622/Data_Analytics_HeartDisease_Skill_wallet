import time
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from backend.analysis import build_charts
from database.database_setup import DB_PATH, initialize_database
from database.queries import (
    alcohol_vs_heart_disease,
    distinct_filter_values,
    gender_distribution,
    smoking_vs_heart_disease,
    summary_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))


@app.before_request
def ensure_database():
    if not DB_PATH.exists():
        initialize_database(force_rebuild=True)


def _filters_from_request() -> dict:
    return {
        "gender": request.args.get("gender", "All"),
        "age_group": request.args.get("age_group", "All"),
        "smoking": request.args.get("smoking", "All"),
        "alcohol": request.args.get("alcohol", "All"),
    }


@app.route("/")
@app.route("/dashboard")
def dashboard():
    filters = distinct_filter_values()
    return render_template("dashboard.html", filters=filters)


@app.route("/story")
def story():
    return render_template("story.html")


@app.route("/performance")
def performance():
    return render_template("performance.html")


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


@app.get("/api/summary")
def api_summary():
    filters = _filters_from_request()
    data = summary_metrics(filters)
    data["gender_distribution"] = gender_distribution(filters)
    data["smoking_vs_heart"] = smoking_vs_heart_disease(filters)
    data["alcohol_vs_heart"] = alcohol_vs_heart_disease(filters)
    return jsonify(data)


@app.get("/api/charts")
def api_charts():
    filters = _filters_from_request()
    return jsonify(build_charts(filters))


@app.get("/api/performance")
def api_performance():
    timings = []
    for _ in range(5):
        start = time.perf_counter()
        _ = summary_metrics({"gender": "All", "age_group": "All", "smoking": "All", "alcohol": "All"})
        timings.append((time.perf_counter() - start) * 1000)

    return jsonify(
        {
            "row_count": summary_metrics()["total_patients"],
            "visualization_count": 10,
            "calculated_fields": 4,
            "avg_query_ms": round(sum(timings) / len(timings), 3),
        }
    )


if __name__ == "__main__":
    initialize_database(force_rebuild=True)
    app.run(debug=True)

