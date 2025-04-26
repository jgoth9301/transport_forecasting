import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def find_database(starting_path: Path, target_name: str) -> Path:
    """
    Recursively search the directory tree starting at starting_path for a file named target_name.
    Returns the first match found or raises a FileNotFoundError if not found.
    """
    for path in starting_path.rglob(target_name):
        return path
    raise FileNotFoundError(f"{target_name} not found in {starting_path}")

# Set the base directory to the parent folder of the current script's directory.
base_dir = Path(__file__).resolve().parent.parent
print(f"Base directory: {base_dir}")

# Search for the database file within the directory tree starting from base_dir.
db_path = find_database(base_dir, 'data_consolidated.db')
print(f"Database found at: {db_path}")

# --- CONNECT TO THE DATABASE ---
conn = sqlite3.connect(db_path)

# --- LOAD DATA ---
df_taxi_data_input = pd.read_sql_query("SELECT Lat, Lon FROM taxi_data_input", conn)
df_taxi_input_model_dbscan = pd.read_sql_query("SELECT Lat, Lon FROM taxi_input_model_dbscan", conn)
df_taxi_input_model_iqr = pd.read_sql_query("SELECT Lat, Lon FROM taxi_input_model_iqr", conn)

# --- CLOSE CONNECTION ---
conn.close()

# --- COMMON AXIS LIMITS ---
x_min, x_max = -75, -72  # Longitude range
y_min, y_max = 39, 43    # Latitude range

# --- PLOT FOR taxi_data_input ---
plt.figure(figsize=(8, 6))
plt.scatter(df_taxi_data_input['Lon'], df_taxi_data_input['Lat'], alpha=0.5, label='taxi_data_input')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Scatter Plot of taxi_data_input")
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.grid(True)
plt.legend(loc='upper right')
plt.show()

# --- PLOT FOR taxi_input_model_dbscan ---
plt.figure(figsize=(8, 6))
plt.scatter(df_taxi_input_model_dbscan['Lon'], df_taxi_input_model_dbscan['Lat'], color='green', alpha=0.5, label='taxi_input_model_dbscan')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Scatter Plot of taxi_input_model_dbscan")
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.grid(True)
plt.legend(loc='upper right')
plt.show()

# --- PLOT FOR taxi_input_model_iqr ---
plt.figure(figsize=(8, 6))
plt.scatter(df_taxi_input_model_iqr['Lon'], df_taxi_input_model_iqr['Lat'], color='orange', alpha=0.5, label='taxi_input_model_iqr')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Scatter Plot of taxi_input_model_iqr")
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.grid(True)
plt.legend(loc='upper right')
plt.show()

