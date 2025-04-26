import sqlite3
from pathlib import Path

# 1) Projekt-Root ist jetzt drei Ebenen über diesem Skript (transport_forecasting)
project_root = Path(__file__).resolve().parents[1]

# 2) Korrigierter Pfad zur DB unter data_ingest/data_input
db_path = project_root / "data_ingest" / "data_consolidated.db"

if not db_path.exists():
    raise FileNotFoundError(f"Datenbank nicht gefunden: {db_path}")

print(f"Verwende Datenbank: {db_path}")

with sqlite3.connect(db_path) as conn:
    cur = conn.cursor()

    # (optional) Tabellen vor dem DROP anzeigen
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tabellen vor DROP:", [r[0] for r in cur.fetchall()])

    # Tabelle löschen
    cur.execute("DROP TABLE IF EXISTS training_set_10_random;")
    conn.commit()
    print("Tabelle 'training_set_10_random' wurde (falls vorhanden) gelöscht.")

    # Tabellen nach dem DROP anzeigen
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tabellen nach DROP:", [r[0] for r in cur.fetchall()])
