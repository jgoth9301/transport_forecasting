import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

def find_database_with_table(starting_path: Path, db_name: str, table_name: str) -> Path:
    """
    Look for all files named db_name under starting_path.
    Return the first one whose sqlite_master lists table_name.
    """
    for candidate in starting_path.rglob(db_name):
        try:
            conn = sqlite3.connect(candidate)
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';",
                conn
            )['name'].tolist()
            conn.close()
            if table_name in tables:
                return candidate
        except Exception:
            # skip files that aren't valid SQLite dbs
            continue
    raise FileNotFoundError(
        f"No '{db_name}' under {starting_path} contains table '{table_name}'"
    )

# 1) Locate the DB that has our table
base_dir = Path(__file__).resolve().parent.parent
db_path  = find_database_with_table(base_dir, "data_consolidated.db", "taxi_input_model_unrestricted")
print(f"▶ Using database: {db_path}")

# 2) Connect & load the table
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM taxi_input_model_unrestricted", conn)
print(f"✅ Loaded {len(df)} rows from taxi_input_model_unrestricted")

# 3) Ensure Lat/Lon numeric & drop invalid
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")
df = df.dropna(subset=["Lat", "Lon"]).copy()

# 4) Compute median location & distance
lat_med = df["Lat"].median()
lon_med = df["Lon"].median()
df["distance_to_med"] = np.sqrt((df["Lat"] - lat_med)**2 + (df["Lon"] - lon_med)**2)

# 5) Compute IQR bounds
q1 = df["distance_to_med"].quantile(0.25)
q3 = df["distance_to_med"].quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr

# 6) Flag outliers in new column 'iqr_outlier'
df["iqr_outlier"] = df["distance_to_med"].apply(
    lambda d: "YES" if (d < lower or d > upper) else "NO"
)

# 7) Write updated taxi_input_model_unrestricted back (with the flag)
to_save = df.drop(columns=["distance_to_med"])
to_save.to_sql("taxi_input_model_unrestricted", conn, if_exists="replace", index=False)
print("📌 Updated 'taxi_input_model_unrestricted' with new column 'iqr_outlier'")

# 8) Export only the non-outliers to taxi_input_model_iqr
inliers = df[df["iqr_outlier"] == "NO"].drop(columns=["distance_to_med", "iqr_outlier"])
inliers.to_sql("taxi_input_model_iqr", conn, if_exists="replace", index=False)
print(f"🚕 Exported {len(inliers)} rows to 'taxi_input_model_iqr'")

conn.close()
