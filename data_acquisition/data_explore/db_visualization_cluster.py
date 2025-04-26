import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# 1) Locate your SQLite DB under the project
project_root = os.path.expanduser("~/PycharmProjects/transport_forecasting")
target_db_base = "data_consolidated"
db_path = None

for root, dirs, files in os.walk(project_root):
    for fn in files:
        name = fn.lower()
        if target_db_base in name and name.endswith((".db", ".sqlite", ".sqlite3")):
            try:
                candidate = os.path.join(root, fn)
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
        f"No valid SQLite DB named like “{target_db_base}.db/.sqlite” under {project_root}"
    )

print("→ Using database:", db_path)

# 2) Load the cluster_coordinates table
conn = sqlite3.connect(db_path)
df = pd.read_sql("SELECT origin, cluster, Lat, Lon, count FROM cluster_coordinates;", conn)
conn.close()

# 3) Compute axis limits from the global min/max of Lat/Lon, ±0.1 buffer
lon_min = df["Lon"].min() - 0.1
lon_max = df["Lon"].max() + 0.1
lat_min = df["Lat"].min() - 0.1
lat_max = df["Lat"].max() + 0.1

# 4) Define colors per origin
color_map = {
    "taxi_data_input":          "blue",
    "taxi_input_model_dbscan":  "green",
    "taxi_input_model_iqr":     "yellow"
}

# 5) Bubble size scale
size_scale = 1e-3

# 6) Plot one bubble chart per origin with identical dynamic axes
for origin, sub in df.groupby("origin"):
    plt.figure(figsize=(8, 6))
    plt.scatter(
        sub["Lon"],
        sub["Lat"],
        s=sub["count"] * size_scale,
        alpha=0.8,
        c=color_map.get(origin, "gray"),
        edgecolors="black",
        linewidth=0.5
    )
    # apply dynamic limits
    plt.xlim(lon_min, lon_max)
    plt.ylim(lat_min, lat_max)

    plt.title(f"Cluster Centroids for {origin}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    # Legend bubble for max size
    max_count = sub["count"].max()
    plt.scatter(
        [], [],
        s=max_count * size_scale,
        c="none",
        edgecolors="black",
        label=f"Max count = {max_count}"
    )
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Bubble size")
    plt.tight_layout()
    plt.show()
