# ============================================================
# dashboard/app.py — Flask Live Air Quality Dashboard
# HOW TO RUN: python dashboard/app.py
# Open: http://localhost:5000
# ============================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify
from python_simulation.sensor_simulator import generate_sensor_data, check_alerts
from python_simulation.data_logger import init_logger, log_reading, get_recent_logs
import threading
import time

app = Flask(__name__)

latest_data   = {}
latest_alerts = []
data_lock     = threading.Lock()
step_counter  = [0]


def background_simulator():
    init_logger()
    while True:
        step_counter[0] += 1
        data   = generate_sensor_data(step_counter[0])
        alerts = check_alerts(data)
        log_reading(data, alerts)

        with data_lock:
            latest_data.update(data)
            latest_alerts[:] = alerts

        time.sleep(3)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/latest")
def api_latest():
    with data_lock:
        return jsonify({
            "data":   dict(latest_data),
            "alerts": list(latest_alerts),
        })


@app.route("/api/history")
def api_history():
    return jsonify(get_recent_logs(50))


t = threading.Thread(target=background_simulator, daemon=True)
t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)