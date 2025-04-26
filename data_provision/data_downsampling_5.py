import sqlite3
import pandas as pd
from pathlib import Path

def find_database(starting_path: Path, target_name: str) -> Path:
    """
    Recursively search the directory tree starting at starting_path for a file named target_name.
    Returns the path to the first match found, or raises a FileNotFoundError if not found.
    """
    for path in starting_path.rglob(target_name):
        return path
    raise FileNotFoundError(f"{target_name} not found in {starting_path}")

# Set the base directory to the parent folder of the current script's directory.
base_dir = Path(__file__).resolve().parent.parent
print(f"Base directory: {base_dir}")

# Locate the database file.
db_path = find_database(base_dir, 'data_consolidated.db')
print(f"Database found at: {db_path}")

# Connect to the database and load data from the taxi_input_model_unrestricted table.
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM taxi_input_model_iqr", conn)
print(f"Loaded {len(df)} rows from table 'taxi_input_model_iqr'.")

# Convert the "Date/Time" column to datetime, ensure Lat/Lon are numeric, and drop rows with missing values.
df['parsed_datetime'] = pd.to_datetime(df['Date/Time'], errors='coerce')
df = df.dropna(subset=['parsed_datetime', 'Lat', 'Lon'])
df['Lat'] = pd.to_numeric(df['Lat'], errors='coerce')
df['Lon'] = pd.to_numeric(df['Lon'], errors='coerce')
df = df.dropna(subset=['Lat', 'Lon'])

# Create a new column 'month' using the parsed_datetime as a Period with monthly granularity.
df['month'] = df['parsed_datetime'].dt.to_period('M')
print("Months found in the data:", df['month'].unique())

# For each month, randomly sample 5% of the rows.
df_sampled = df.groupby('month', group_keys=False).apply(lambda x: x.sample(frac=0.05, random_state=42))
print(f"Sampled {len(df_sampled)} rows (10% per month).")

# Convert the 'month' column from a Period type to string, as sqlite3 doesn't support Period directly.
df_sampled['month'] = df_sampled['month'].astype(str)

# Write the sampled data to a new table called training_set_10%_random.
df_sampled.to_sql('training_set_5_random_blue', conn, if_exists='replace', index=False)
print("Sampled data written to table 'training_set_5_random_blue'.")

# Close the database connection.
conn.close()
