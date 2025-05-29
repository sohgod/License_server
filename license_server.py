from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# ✅ ایجاد دیتابیس و جدول در صورت عدم وجود
def init_db():
    conn = sqlite3.connect("licenses.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT UNIQUE,
        cpu_id TEXT,
        used BOOLEAN DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()

# ✅ فراخوانی ساخت دیتابیس
init_db()

# ✅ تابع اتصال به دیتابیس
def get_db():
    conn = sqlite3.connect("licenses.db")
    conn.row_factory = sqlite3.Row
    return conn

# ✅ API بررسی اعتبار لایسنس
@app.route("/validate", methods=["POST"])
def validate_license():
    data = request.get_json()
    license_key = data.get("license_key")
    cpu_id = data.get("cpu_id")

    if not license_key or not cpu_id:
        return jsonify({"status": "error", "message": "Missing license_key or cpu_id"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,))
    row = cur.fetchone()

    if not row:
        return jsonify({"status": "error", "message": "Invalid license key"}), 404

    if row["used"] and row["cpu_id"] != cpu_id:
        return jsonify({"status": "error", "message": "License already used on another device"}), 403

    if not row["used"]:
        cur.execute("UPDATE licenses SET used = 1, cpu_id = ? WHERE license_key = ?", (cpu_id, license_key))
        conn.commit()

    return jsonify({"status": "ok", "message": "License is valid"}), 200

# ✅ اجرای سرور
if __name__ == "__main__":
    app.run(debug=True, port=5000)
