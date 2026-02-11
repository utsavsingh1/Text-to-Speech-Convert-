from flask import Flask, render_template, request, jsonify, send_file
import pyttsx3
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('tts_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT,
                  voice TEXT,
                  rate INTEGER,
                  volume REAL,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_voices', methods=['GET'])
def get_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice_list = [{'id': v.id, 'name': v.name} for v in voices]
    engine.stop()
    return jsonify(voice_list)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    text = data.get('text', '')
    voice_id = data.get('voice', '')
    rate = int(data.get('rate', 150))
    volume = float(data.get('volume', 1.0))
    
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    
    output_file = 'output.mp3'
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    
    conn = sqlite3.connect('tts_history.db')
    c = conn.cursor()
    c.execute("INSERT INTO history (text, voice, rate, volume, timestamp) VALUES (?, ?, ?, ?, ?)",
              (text, voice_id, rate, volume, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'file': output_file})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    voice_id = data.get('voice', '')
    rate = int(data.get('rate', 150))
    volume = float(data.get('volume', 1.0))
    
    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    engine.say(text)
    engine.runAndWait()
    
    return jsonify({'success': True})

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('tts_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    
    history = [{'id': r[0], 'text': r[1], 'voice': r[2], 'rate': r[3], 'volume': r[4], 'timestamp': r[5]} for r in rows]
    return jsonify(history)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
