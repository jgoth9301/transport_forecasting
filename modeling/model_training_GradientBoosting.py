import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
import mlflow
import mlflow.sklearn
import holidays
import shap
import matplotlib.pyplot as plt

# ─── Config ─────────────────────────────────────────────────────────────
expected_table = "training_set_10_random_blue"
output_csv_path = r"/modeling\cluster_metrics_summary_GradientBoosting.csv"
shap_output_dir = r"/modeling\cluster_shap_outputs"
country_code = "DE"  # e.g. 'DE' for Germany

gb_param_grid = {
    "learning_rate": [0.01, 0.1],
    "max_iter": [100, 300],
    "max_depth": [3, 5],
}

# ✅ Full Feature Set
features = ['day', 'hour', 'special_day', 'weekend_hour_interaction']

# ─── Locate .db file ────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = None
for root, dirs, files in os.walk(project_root):
    for fn in files:
        if "data_consolidated" in fn.lower() and fn.lower().endswith((".db", ".sqlite", ".sqlite3")):
            candidate = os.path.join(root, fn)
            with sqlite3.connect(candidate) as conn:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table';", conn
                )['name'].tolist()
            if expected_table in tables:
                db_path = candidate
                break
    if db_path:
        break

if not db_path:
    raise FileNotFoundError(f"No DB under {project_root!r} contains table '{expected_table}'")
print(f"▶ Using database file: {db_path}")

# ─── Load & preprocess ─────────────────────────────────────────────────
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query(f"SELECT * FROM {expected_table}", conn)

df['parsed_datetime'] = pd.to_datetime(df["Date/Time"])
df['day'] = df['parsed_datetime'].dt.day
df['hour'] = df['parsed_datetime'].dt.hour

# ─── Special day encoding ──────────────────────────────────────────────
def assign_special_day(date_series, country="DE"):
    holiday_dates = holidays.country_holidays(country)
    return np.where(
        date_series.dt.date.isin(holiday_dates), 3,
        np.where(date_series.dt.weekday == 5, 1,
                 np.where(date_series.dt.weekday == 6, 2, 0))
    )

df['special_day'] = assign_special_day(df['parsed_datetime'], country=country_code)

# ─── Create weekend-hour interaction ────────────────────────────────────
df['is_weekend'] = df['special_day'].isin([1, 2]).astype(int)
df['weekend_hour_interaction'] = df['is_weekend'] * df['hour']

# ─── Grouping for Model Input ──────────────────────────────────────────
df_counts = (
    df.groupby(['cluster', 'day', 'hour', 'special_day', 'weekend_hour_interaction'])
    .size()
    .reset_index(name='count')
)

# ─── MLflow Setup ───────────────────────────────────────────────────────
mlflow.set_experiment("Taxi_Demand_Per_Cluster")
mlflow.sklearn.autolog(disable=True)
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
os.makedirs(shap_output_dir, exist_ok=True)

# ─── Train per-cluster model + SHAP ─────────────────────────────────────
metrics_summary = []

for cluster_id, grp in df_counts.groupby('cluster'):
    X = grp[features]
    y = grp['count']

    with mlflow.start_run(run_name=f"cluster_{cluster_id}"):
        grid = GridSearchCV(
            HistGradientBoostingRegressor(loss="poisson"),
            param_grid=gb_param_grid,
            scoring='neg_mean_absolute_error',
            cv=5,
            n_jobs=-1
        )
        grid.fit(X, y)

        best_model = grid.best_estimator_
        best_params = grid.best_params_
        mlflow.log_params(best_params)

        cv_mae = -cross_val_score(
            best_model, X, y,
            scoring='neg_mean_absolute_error',
            cv=5
        ).mean()
        mlflow.log_metric("cv_mae", cv_mae)

        mlflow.sklearn.log_model(
            sk_model=best_model,
            artifact_path=f"model_cluster_{cluster_id}"
        )

        explainer = shap.Explainer(best_model, X)
        shap_values = explainer(X)

        plt.figure()
        shap.summary_plot(shap_values, X, show=False)
        plt.title(f"SHAP Summary - Cluster {cluster_id}")
        plt.tight_layout()
        plt.savefig(os.path.join(shap_output_dir, f"shap_cluster_{cluster_id}.png"))
        plt.close()

    metrics_summary.append({
        "cluster_id": cluster_id,
        **best_params,
        "cv_mae": cv_mae
    })

# ─── Save Summary ───────────────────────────────────────────────────────
metrics_df = pd.DataFrame(metrics_summary)
metrics_df.to_csv(output_csv_path, index=False)
print(f"▶ Saved metrics summary to: {output_csv_path}")
print(f"▶ SHAP plots saved to: {shap_output_dir}")
