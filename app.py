from flask import Flask, request, jsonify, send_file
import random, string
import sqlite3
from datetime import datetime
import pyshorteners
import qrcode
import io

app = Flask(__name__)

# =========================
# DATABASE + TRACKING
# =========================
def init_db():
    conn = sqlite3.connect("usage.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        endpoint TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def log_usage(endpoint):
    conn = sqlite3.connect("usage.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO logs (endpoint, timestamp) VALUES (?, ?)",
        (endpoint, datetime.now())
    )

    conn.commit()
    conn.close()

@app.before_request
def track_all_requests():
    log_usage(request.path)

# =========================
# ROUTES
# =========================

# Home
@app.route('/')
def home():
    return {"message": "Tiny Tools API is live"}

# Password Generator
@app.route('/generate-password')
def generate_password():
    length = int(request.args.get('length', 12))
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return {"password": password}

# URL Shortener
@app.route('/shorten-url')
def shorten_url():
    url = request.args.get('url')
    if not url:
        return {"error": "URL required"}, 400

    try:
        s = pyshorteners.Shortener()
        short_url = s.tinyurl.short(url)
        return {"original": url, "short_url": short_url}
    except Exception as e:
        return {"error": str(e)}, 500

# QR Code Generator
@app.route('/qr')
def generate_qr():
    text = request.args.get('text')
    if not text:
        return {"error": "Text required"}, 400

    qr = qrcode.make(text)

    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

# View Logs
@app.route('/logs')
def get_logs():
    conn = sqlite3.connect("usage.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")
    data = cursor.fetchall()

    conn.close()
    return {"logs": data}

# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)