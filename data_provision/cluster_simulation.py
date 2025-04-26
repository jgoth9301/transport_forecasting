import os
import sqlite3
import pandas as pd
from sklearn.cluster import KMeans

# 1) Project root (no hard‑coded “C:”)
project_root = os.path.expanduser("~/PycharmProjects/transport_forecasting")

# 2) Locate the correct SQLite DB file
target_db_base = "data_consolidated"
db_path = None
for root, dirs, files in os.walk(project_root):
    for fn in files:
        name = fn.lower()
        if target_db_base in name and name.endswith((".db", ".sqlite", ".sqlite3")):
            candidate = os.path.join(root, fn)
            try:
                tmp = sqlite3.connect(candidate)
                tmp.execute("SELECT name FROM sqlite_master LIMIT 1;")
                tmp.close()
                db_path = candidate
                break
            except sqlite3.DatabaseError:
                continue
    if db_path:
        break

if not db_path:
    raise FileNotFoundError(
        f"Could not find a valid SQLite DB named like “{target_db_base}.db/.sqlite” under {project_root}"
    )

print("→ Using database:", db_path)

# 3) Define the tables to cluster
tables = [
    "taxi_input_model_unrestricted",
    "taxi_input_model_iqr"
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 4) Ensure cluster_coordinates table exists (clear any existing entries)
cur.execute("""
CREATE TABLE IF NOT EXISTS cluster_coordinates (
    origin TEXT,
    cluster INTEGER,
    Lat REAL,
    Lon REAL,
    count INTEGER
);
""")
cur.execute("DELETE FROM cluster_coordinates;")

all_centroids = []

# 5) Process each table in turn
for tbl in tables:
    print(f"→ Processing table: {tbl}")

    # 5a) Add 'cluster' column if missing
    cur.execute(f"PRAGMA table_info({tbl});")
    cols = [c[1] for c in cur.fetchall()]
    if "cluster" not in cols:
        cur.execute(f"ALTER TABLE {tbl} ADD COLUMN cluster INTEGER;")

    # 5b) Load data
    df = pd.read_sql(f"SELECT rowid, Lat, Lon FROM {tbl};", conn)

    # 5c) Run KMeans(n=10)
    coords = df[["Lat", "Lon"]]
    km = KMeans(n_clusters=10, random_state=42)
    df["cluster"] = km.fit_predict(coords) + 1  # labels 1–10

    # 5d) Write back cluster labels
    for _, row in df.iterrows():
        cur.execute(
            f"UPDATE {tbl} SET cluster = ? WHERE rowid = ?;",
            (int(row["cluster"]), int(row["rowid"]))
        )

    # 5e) Compute centroids & counts, collect for insertion
    cent = (
        df.groupby("cluster")
          .agg(count=("rowid", "size"),
               Lat=("Lat", "mean"),
               Lon=("Lon", "mean"))
          .reset_index()
    )
    cent["origin"] = tbl
    all_centroids.append(cent[["origin", "cluster", "Lat", "Lon", "count"]])

# 6) Concatenate all centroids and insert into cluster_coordinates
all_centroids_df = pd.concat(all_centroids, ignore_index=True)

for _, row in all_centroids_df.iterrows():
    cur.execute(
        "INSERT INTO cluster_coordinates (origin, cluster, Lat, Lon, count) VALUES (?, ?, ?, ?, ?);",
        (
            row["origin"],
            int(row["cluster"]),
            float(row["Lat"]),
            float(row["Lon"]),
            int(row["count"])
        )
    )

# 7) Commit & close
conn.commit()
conn.close()

print("✅ Done: clusters assigned in all tables and cluster_coordinates populated (30 rows).")
