
# app/database.py
import sqlite3
from pathlib import Path

# Save the database file in the root of the backend folder
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "telemetry.db"

def init_db():
    """Creates the database and the alerts table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create a table with the exact shape of the Pydantic model
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            machine_id TEXT NOT NULL,
            error_code TEXT NOT NULL,
            temperature REAL NOT NULL,
            vibration REAL NOT NULL,     
            pressure REAL NOT NULL,      
            severity TEXT NOT NULL       
        )
    ''')
    conn.commit()
    conn.close()

def insert_alert(machine_id: str, error_code: str, temperature: float, vibration: float, pressure: float, severity: str):
    """Inserts a clean, validated alert into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (machine_id, error_code, temperature, vibration, pressure, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (machine_id, error_code, temperature, vibration, pressure, severity))
    conn.commit()
    conn.close()