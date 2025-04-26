import os
import sqlite3
import pandas as pd

# 1) Locate your SQLite DB under the project root
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

# 2) Connect and pull counts per cluster from each table
conn = sqlite3.connect(db_path)

df_input = pd.read_sql_query(
    "SELECT cluster, COUNT(*) AS count_input "
    "FROM taxi_data_input GROUP BY cluster;",
    conn
)
df_dbscan = pd.read_sql_query(
    "SELECT cluster, COUNT(*) AS count_dbscan "
    "FROM taxi_input_model_dbscan GROUP BY cluster;",
    conn
)
df_iqr = pd.read_sql_query(
    "SELECT cluster, COUNT(*) AS count_iqr "
    "FROM taxi_input_model_iqr GROUP BY cluster;",
    conn
)
df_coords = pd.read_sql_query(
    "SELECT cluster, SUM(count) AS coord_count "
    "FROM cluster_coordinates GROUP BY cluster;",
    conn
)

conn.close()

# 3) Merge into a single DataFrame for clusters 1–10
clusters = pd.DataFrame({'cluster': range(1, 11)})

result = (
    clusters
    .merge(df_input,  on='cluster', how='left')
    .merge(df_dbscan, on='cluster', how='left')
    .merge(df_iqr,    on='cluster', how='left')
    .merge(df_coords, on='cluster', how='left')
)

# 4) Fill missing with 0
result = result.fillna(0).astype({
    'count_input':   int,
    'count_dbscan':  int,
    'count_iqr':     int,
    'coord_count':   int
})

# 5) Compute:
#    col5 = sum of the three table‐counts
#    col6 = coord_count (from cluster_coordinates)
#    col7 = coord_count − sum_of_three
result['sum_tables'] = (
    result['count_input']
  + result['count_dbscan']
  + result['count_iqr']
)
result['diff'] = result['coord_count'] - result['sum_tables']

# 6) Rename columns for clarity (optional)
result = result.rename(columns={
    'cluster':      'Cluster',
    'count_input':  'Count_Input',
    'count_dbscan': 'Count_DBSCAN',
    'count_iqr':    'Count_IQR',
    'sum_tables':   'Sum_Tables_1_2_3',
    'coord_count':  'Count_Coordinates',
    'diff':         'Coordinates_minus_Sum'
})

# 7) Display the final table
print(result)
