from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_FILE = "workout_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            routine_name TEXT NOT NULL
        )
    ''')
    
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

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINTS ---

@app.route('/api/sessions', methods=['POST'])
def create_session_endpoint():
    data = request.get_json() or {}
    routine_name = data.get('routine_name')
    
    if not routine_name:
        return jsonify({'error': 'Nome scheda mancante'}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute('INSERT INTO sessions (date, routine_name) VALUES (?, ?)', (today_str, routine_name))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'session_id': session_id, 'routine_name': routine_name}), 201

@app.route('/api/sets', methods=['POST'])
def save_set_endpoint():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    exercise_name = data.get('exercise_name')
    set_number = data.get('set_number')
    weight_kg = data.get('weight_kg')
    reps = data.get('reps')
    rpe = data.get('rpe')
    
    if not all([session_id, exercise_name, set_number, weight_kg, reps]):
        return jsonify({'error': 'Dati incompleti'}), 400

    now_str = datetime.now().strftime("%H:%M:%S")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO workout_sets (session_id, exercise_name, set_number, weight_kg, reps, rpe, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, exercise_name, set_number, weight_kg, reps, rpe, now_str))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

@app.route('/api/sets', methods=['GET'])
def get_session_sets_endpoint():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify([])
        
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, exercise_name, set_number, weight_kg, reps, rpe, timestamp 
        FROM workout_sets 
        WHERE session_id = ? 
        ORDER BY id DESC
    ''', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/sets/<int:set_id>', methods=['DELETE'])
def delete_set_endpoint(set_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM workout_sets WHERE id = ?', (set_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': set_id})

@app.route('/api/history', methods=['GET'])
def get_history_endpoint():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT w.id, s.date, s.routine_name, w.exercise_name, w.set_number, w.weight_kg, w.reps, w.rpe
        FROM workout_sets w
        JOIN sessions s ON w.session_id = s.id
        ORDER BY w.id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)