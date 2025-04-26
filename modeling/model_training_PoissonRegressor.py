import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import PoissonRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
import mlflow
import mlflow.sklearn
import holidays

# ─── Config ─────────────────────────────────────────────────────────────
expected_table = "training_set_10_random_blue"
param_grid = {
    "alpha":    [1e-8, 1e-6, 1e-4, 1e-2, 1e-1],
    "max_iter": [100, 300, 500]
}
output_csv_path = r"/modeling\cluster_metrics_summary_PoissonRegressor.csv"
country_code = "DE"  # Germany for public holidays

# ─── Find the database ───────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = None

for root, dirs, files in os.walk(project_root):
    for fn in files:
        if "data_consolidated" in fn.lower() and fn.lower().endswith((".db", ".sqlite", ".sqlite3")):
            candidate = os.path.join(root, fn)
            with sqlite3.connect(candidate) as conn:
                existing_tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table';", conn
                )['name'].tolist()
            if expected_table in existing_tables:
                db_path = candidate
                break
    if db_path:
        break

if not db_path:
    raise FileNotFoundError(
        f"No database file under {project_root!r} contains the table '{expected_table}'."
    )

print(f"▶ Using database file: {db_path}")

# ─── Load data ──────────────────────────────────────────────────────────
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query(f"SELECT * FROM {expected_table}", conn)

# ─── Feature engineering ────────────────────────────────────────────────
df['parsed_datetime'] = pd.to_datetime(df["Date/Time"])
df['day'] = df['parsed_datetime'].dt.day
df['hour'] = df['parsed_datetime'].dt.hour

def assign_special_day(date_series, country="DE"):
    holiday_dates = holidays.country_holidays(country)
    special_days = np.where(
        date_series.dt.date.isin(holiday_dates),
        3,  # Public Holiday
        np.where(
            date_series.dt.weekday == 5,  # Saturday
            1,
            np.where(
                date_series.dt.weekday == 6,  # Sunday
                2,
                0  # Weekday (Mon-Fri)
            )
        )
    )
    return special_days

df['special_day'] = assign_special_day(df['parsed_datetime'], country=country_code)

df_counts = (
    df.groupby(['cluster', 'day', 'hour', 'special_day'])
      .size()
      .reset_index(name='count')
)

# ─── MLflow setup ───────────────────────────────────────────────────────
mlflow.set_experiment("Taxi_Demand_Per_Cluster")
mlflow.sklearn.autolog(disable=True)

# ─── Train one PoissonRegressor per cluster ─────────────────────────────
metrics_summary = []
models = {}

for cluster_id, grp in df_counts.groupby('cluster'):
    X = grp[['day', 'hour', 'special_day']]
    y = grp['count']

    with mlflow.start_run(run_name=f"cluster_{cluster_id}"):
        # Hyperparameter search
        grid = GridSearchCV(
            estimator=PoissonRegressor(),
            param_grid=param_grid,
            scoring='neg_mean_absolute_error',
            cv=5,
            n_jobs=-1
        )
        grid.fit(X, y)

        # Log best parameters
        best_params = grid.best_params_
        mlflow.log_params(best_params)

        # Train final model with best parameters
        model = PoissonRegressor(**best_params)
        model.fit(X, y)

        # Compute and log CV-MAE
        cv_mae = -cross_val_score(
            model, X, y,
            scoring='neg_mean_absolute_error',
            cv=5
        ).mean()
        mlflow.log_metric("cv_mae", cv_mae)

        # Save the tuned model as an MLflow artifact
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=f"model_cluster_{cluster_id}"
        )

    # Store metrics for CSV
    metrics_summary.append({
        "cluster_id": cluster_id,
        "alpha":      best_params["alpha"],
        "max_iter":   best_params["max_iter"],
        "cv_mae":     cv_mae
    })
    models[cluster_id] = model

# ─── Write summary CSV ──────────────────────────────────────────────────
out_dir = os.path.dirname(output_csv_path)
os.makedirs(out_dir, exist_ok=True)

metrics_df = pd.DataFrame(metrics_summary)
metrics_df.to_csv(output_csv_path, index=False)
print(f"▶ Saved cluster metrics summary to: {output_csv_path}")

