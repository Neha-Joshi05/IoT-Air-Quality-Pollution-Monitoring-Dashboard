# ============================================================
# data_logger.py — CSV Data Logger
# PURPOSE: Saves every sensor reading with UTF-8 encoding.
# ============================================================

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "..", "data", "air_quality_log.csv")

HEADERS = [
    "timestamp", "pm25", "pm10", "gas_index", "co2_ppm",
    "temperature", "humidity", "aqi", "category", "alerts"
]


def init_logger():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HEADERS).writeheader()


def log_reading(data: dict, alerts: list):
    # Strip non-ASCII characters to avoid Windows encoding issues
    clean_alerts = []
    for a in alerts:
        clean = a.encode("ascii", "ignore").decode("ascii").strip()
        clean_alerts.append(clean if clean else a)

    row = {
        "timestamp":   data["timestamp"],
        "pm25":        data["pm25"],
        "pm10":        data["pm10"],
        "gas_index":   data["gas_index"],
        "co2_ppm":     data["co2_ppm"],
        "temperature": data["temperature"],
        "humidity":    data["humidity"],
        "aqi":         data["aqi"],
        "category":    data["category"],
        "alerts":      " | ".join(clean_alerts) if clean_alerts else "None",
    }
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=HEADERS).writerow(row)


def get_recent_logs(n=50):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-n:]