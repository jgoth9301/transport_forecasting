import pandas as pd
import sqlite3
from pathlib import Path
import holidays

# --- CONFIGURATION ---

input_dir    = Path(__file__).parent / 'data_input'
output_db    = Path(__file__).parent / 'data_consolidated.db'
table_name   = 'taxi_input_model_unrestricted'

# --- FIND CSV FILES ---

csv_files = list(input_dir.glob('*.csv'))
print(f'Found {len(csv_files)} CSV file(s) in: {input_dir}')
for f in csv_files:
    print(f' - {f.name}')

if not csv_files:
    print("⚠️ No CSV files found. Exiting.")
    exit()

# --- LOAD DATA WITH FILE SOURCE COLUMN ---

df_list = []
for file in csv_files:
    try:
        df = pd.read_csv(file)
        df['source_file'] = file.name  # add source info
        df_list.append(df)
    except Exception as e:
        print(f"❌ Failed to read {file.name}: {e}")

if not df_list:
    print("⚠️ No valid CSV files loaded. Exiting.")
    exit()

combined_df = pd.concat(df_list, ignore_index=True)
print(f'\n✅ Combined {len(df_list)} files into {combined_df.shape[0]} rows.')

# --- ADD "special_day" COLUMN ---

# parse Date/Time into datetime
combined_df['parsed_datetime'] = pd.to_datetime(combined_df["Date/Time"])

# prepare US holiday calendar
us_holidays = holidays.US()

# function to label each date
def label_special_day(dt):
    date_only = dt.date()
    if date_only in us_holidays:
        return "Public Holiday"
    weekday = dt.weekday()
    if weekday == 5:
        return "Saturday"
    elif weekday == 6:
        return "Sunday"
    else:
        return "Weekday"

combined_df['special_day'] = combined_df['parsed_datetime'].apply(label_special_day)

# drop helper column
combined_df.drop(columns=['parsed_datetime'], inplace=True)

# --- CREATE TABLE WITH TYPES IN SQLITE ---

conn   = sqlite3.connect(output_db)
cursor = conn.cursor()

# Drop table if exists and create with explicit types, including special_day
cursor.execute(f'''
    DROP TABLE IF EXISTS {table_name}
''')
cursor.execute(f'''
    CREATE TABLE {table_name} (
        [Date/Time]   TEXT,
        Lat           REAL,
        Lon           REAL,
        Base          TEXT,
        source_file   TEXT,
        special_day   TEXT
    )
''')
conn.commit()

# --- WRITE DATA TO TABLE ---

combined_df.to_sql(table_name, conn, if_exists='append', index=False)
conn.close()

print(f'\n📦 Data written to database: {output_db}')
print(f'    Table: "{table_name}" with columns Date/Time, Lat, Lon, Base, source_file, special_day.')
