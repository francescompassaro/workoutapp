import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "workout_data.db"

def init_db():
    """Inizializza le tabelle nel database se non esistono."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabella Sessioni / Allenamenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            routine_name TEXT NOT NULL
        )
    ''')
    
    # Tabella Set / Serie registrate
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            exercise_name TEXT NOT NULL,
            set_number INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            reps INTEGER NOT NULL,
            rpe REAL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(routine_name: str) -> int:
    """Crea una nuova sessione e restituisce l'ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('INSERT INTO sessions (date, routine_name) VALUES (?, ?)', (today_str, routine_name))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def save_set(session_id: int, exercise_name: str, set_number: int, weight: float, reps: int, rpe: float):
    """Salva una singola serie completata."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%H:%M:%S")
    cursor.execute('''
        INSERT INTO workout_sets (session_id, exercise_name, set_number, weight_kg, reps, rpe, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, exercise_name, set_number, weight, reps, rpe, now_str))
    conn.commit()
    conn.close()

def get_session_sets(session_id: int) -> pd.DataFrame:
    """Recupera le serie della sessione corrente sotto forma di DataFrame Pandas."""
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT 
            exercise_name AS Esercizio, 
            set_number AS Num_Set, 
            weight_kg AS Kg, 
            reps AS Reps, 
            rpe AS RPE, 
            timestamp AS Ora 
        FROM workout_sets 
        WHERE session_id = ? 
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return df

def get_all_history() -> pd.DataFrame:
    """Recupera lo storico completo degli allenamenti."""
    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT 
            s.date AS Data, 
            s.routine_name AS Scheda, 
            w.exercise_name AS Esercizio, 
            w.set_number AS Num_Set, 
            w.weight_kg AS Kg, 
            w.reps AS Reps, 
            w.rpe AS RPE
        FROM workout_sets w
        JOIN sessions s ON w.session_id = s.id
        ORDER BY w.id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df