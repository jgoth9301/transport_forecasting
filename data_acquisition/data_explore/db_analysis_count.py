import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def find_database(starting_path: Path, target_name: str) -> Path:
    """
    Recursively search the directory tree starting at starting_path for a file named target_name.
    Returns the first match found, or raises a FileNotFoundError if not found.
    """
    for path in starting_path.rglob(target_name):
        return path
    raise FileNotFoundError(f"{target_name} not found in {starting_path}")

# Instead of using the directory of the current script, use its parent directory.
# This assumes that both data_explore and data_ingest (with data_consolidated.db)
# are subfolders of the same parent directory.
base_dir = Path(__file__).resolve().parent.parent
print(f"Base directory: {base_dir}")

# Search for the database file in the directory tree starting at base_dir.
db_path = find_database(base_dir, 'data_consolidated.db')
print(f"Database found at: {db_path}")

# --- CONNECT TO DATABASE ---
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# --- TABLES TO CHECK ---
tables = ['taxi_input_model_unrestricted', 'taxi_input_model_dbscan', 'training_set_10_random']

# We'll collect our statistics here for the final consolidated table and chart.
stats_dict = {}

# --- LOOP THROUGH TABLES ---
for table in tables:
    print(f"\n🔍 Analyzing table: {table}")

    # Count rows and store the count
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"📊 Row count: {count}")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Error accessing table '{table}': {e}")
        continue

    # Load data into pandas and calculate descriptive statistics.
    try:
        df = pd.read_sql_query(f"SELECT Lat, Lon FROM {table}", conn)

        if df.empty:
            print("⚠️ No data to analyze.")
            continue

        # Calculate descriptive statistics for latitude and longitude.
        lat_min = df['Lat'].min()
        lat_max = df['Lat'].max()
        lat_median = df['Lat'].median()

        lon_min = df['Lon'].min()
        lon_max = df['Lon'].max()
        lon_median = df['Lon'].median()

        # Print results for this table.
        print(f"🧭 Latitude   → min: {lat_min:.6f}, max: {lat_max:.6f}, median: {lat_median:.6f}")
        print(f"🧭 Longitude  → min: {lon_min:.6f}, max: {lon_max:.6f}, median: {lon_median:.6f}")

        # Store results for each table in a dictionary, including the row count.
        stats_dict[table] = {
            'Row_count': count,
            'Lat_min': lat_min,
            'Lat_max': lat_max,
            'Lat_median': lat_median,
            'Lon_min': lon_min,
            'Lon_max': lon_max,
            'Lon_median': lon_median
        }

    except Exception as e:
        print(f"❌ Error reading data from {table}: {e}")

# --- CLOSE CONNECTION ---
conn.close()

# --- CREATE A CONSOLIDATED TABLE (DataFrame) ---
if stats_dict:
    df_stats = pd.DataFrame(stats_dict).T  # Transpose so that each table is a row
    print("\n===== CONSOLIDATED STATISTICS =====")
    print(df_stats)

    # --- CREATE A CLUSTERED BAR CHART WITH SECONDARY AXIS ---
    # Plot the latitude and longitude descriptive statistics as a bar chart.
    fig, ax1 = plt.subplots(figsize=(10, 6))
    stat_columns = ['Lat_min', 'Lat_max', 'Lat_median', 'Lon_min', 'Lon_max', 'Lon_median']
    df_stats[stat_columns].plot(kind='bar', ax=ax1)
    ax1.set_xlabel("Table")
    ax1.set_ylabel("Value")
    ax1.set_title("Consolidated Statistics (Min, Max, Median) for All Tables")
    ax1.grid(True)

    # Create secondary axis for the row count line chart.
    ax2 = ax1.twinx()
    ax2.plot(df_stats.index, df_stats['Row_count'], color='black', marker='o', linestyle='-', linewidth=2, label='Row Count')
    ax2.set_ylabel("Row Count")
    ax2.legend(loc='upper left')

    plt.tight_layout()  # Adjust layout to avoid overlap
    plt.show()
else:
    print("\nNo statistics to plot—no data was found in the specified tables.")
