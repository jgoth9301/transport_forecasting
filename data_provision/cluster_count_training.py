import sqlite3
import pandas as pd
from pathlib import Path

# Define the path to the SQLite database
db_path = r"/data_acquisition\data_ingest\data_consolidated.db"
table_name = "training_set_10_random_blue"

# 🔌 Connect to the SQLite database
conn = sqlite3.connect(db_path)

# 🧮 SQL query: Count number of rows per cluster
query = f"""
    SELECT cluster, COUNT(*) AS row_count
    FROM {table_name}
    GROUP BY cluster
    ORDER BY row_count DESC
"""

# 📊 Load result into a DataFrame
df_counts = pd.read_sql_query(query, conn)

# ✅ Now display the results
print(df_counts)

# 🔒 Close the connection
conn.close()
