import sqlite3
from pathlib import Path

def find_database(starting_path: Path, target_name: str) -> Path:
    """
    Recursively search the directory tree starting at starting_path for a file
    named target_name. Returns the path to the first match found, or raises a
    FileNotFoundError if not found.
    """
    for path in starting_path.rglob(target_name):
        return path
    raise FileNotFoundError(f"{target_name} not found in {starting_path}")

# Set the base directory to the parent folder of the current script
base_dir = Path(__file__).resolve().parent.parent
print(f"Base directory: {base_dir}")

# Locate the database file 'data_consolidated.db' in the project
db_path = find_database(base_dir, 'data_consolidated.db')
print(f"Database found at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# SQL command to drop (delete) the table "taxi_input_model_dbscan""
# The table name is enclosed in double quotes because of the special character (%).
drop_table_query = 'DROP TABLE IF EXISTS "taxi_data_input"'

try:
    cursor.execute(drop_table_query)
    conn.commit()
    print('Table "taxi_input_model_dbscan" deleted successfully (if it existed).')
except Exception as e:
    print("Error deleting table:", e)
finally:
    conn.close()
