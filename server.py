from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tts_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT NOT NULL,
                  voice TEXT,
                  rate REAL,
                  pitch REAL,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/save', methods=['POST'])
def save_history():
    data = request.json
    conn = sqlite3.connect('tts_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (text, voice, rate, pitch, timestamp) VALUES (?, ?, ?, ?, ?)",
              (data['text'], data['voice'], data['rate'], data['pitch'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('tts_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    history = [{'id': r[0], 'text': r[1], 'voice': r[2], 'rate': r[3], 'pitch': r[4], 'timestamp': r[5]} for r in rows]
    return jsonify(history)

@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete_history(id):
    conn = sqlite3.connect('tts_database.db')
    c = conn.cursor()
    c.execute("DELETE FROM history WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
