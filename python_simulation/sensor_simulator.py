# ============================================================
# sensor_simulator.py — Virtual Air Quality Sensor Simulator
# PURPOSE: Simulates MQ135, PM2.5, PM10, DHT22 sensor data.
# INTERVIEW TIP: "MQ135 measures gases like CO2, NH3, NOx.
#                 PM2.5 measures fine particulate matter —
#                 particles smaller than 2.5 micrometers
#                 which penetrate deep into lungs."
# ============================================================

import random
import math
from datetime import datetime

# ── AQI Breakpoints for PM2.5 (US EPA Standard) ──────────────
# INTERVIEW TIP: "AQI is calculated using EPA breakpoint tables.
#                 Each pollutant has its own breakpoints."
AQI_BREAKPOINTS = [
    # (C_low, C_high, I_low, I_high, category, color)
    (0.0,  12.0,   0,  50,  "Good",            "#00e400"),
    (12.1, 35.4,  51, 100,  "Moderate",         "#ffff00"),
    (35.5, 55.4, 101, 150,  "Unhealthy for Sensitive", "#ff7e00"),
    (55.5,150.4, 151, 200,  "Unhealthy",        "#ff0000"),
    (150.5,250.4,201, 300,  "Very Unhealthy",   "#8f3f97"),
    (250.5,500.4,301, 500,  "Hazardous",        "#7e0023"),
]

# ── Simulation Scenarios ──────────────────────────────────────
SCENARIOS = ["good", "moderate", "unhealthy", "hazardous"]


def calculate_aqi(pm25: float) -> tuple:
    """
    Calculates AQI from PM2.5 concentration using EPA formula.
    Formula: AQI = ((I_hi - I_lo) / (C_hi - C_lo)) * (C - C_lo) + I_lo
    INTERVIEW TIP: "This is the standard EPA AQI formula —
                    real systems use this exact calculation."
    Returns: (aqi_value, category, color)
    """
    for c_lo, c_hi, i_lo, i_hi, category, color in AQI_BREAKPOINTS:
        if c_lo <= pm25 <= c_hi:
            aqi = ((i_hi - i_lo) / (c_hi - c_lo)) * (pm25 - c_lo) + i_lo
            return round(aqi), category, color

    # Beyond hazardous
    return 500, "Hazardous", "#7e0023"


def generate_sensor_data(time_step: int) -> dict:
    """
    Generates one reading from all virtual air quality sensors.
    Cycles through Good → Moderate → Unhealthy → Hazardous
    every 25 steps to demonstrate all alert levels.
    """
    scenario = SCENARIOS[(time_step // 25) % len(SCENARIOS)]

    # ── PM2.5 (µg/m³) ─────────────────────────────────────────
    pm25_ranges = {
        "good":      (2,   10),
        "moderate":  (13,  34),
        "unhealthy": (56,  140),
        "hazardous": (260, 400),
    }
    pm25 = round(random.uniform(*pm25_ranges[scenario]) +
                 2 * math.sin(time_step / 10), 1)
    pm25 = max(0, pm25)

    # ── PM10 (µg/m³) — coarse particles ───────────────────────
    pm10 = round(pm25 * random.uniform(1.5, 2.2), 1)

    # ── MQ135 — gas index (0–1023 ADC raw value) ──────────────
    gas_ranges = {
        "good":      (50,  150),
        "moderate":  (151, 300),
        "unhealthy": (301, 500),
        "hazardous": (501, 900),
    }
    gas_index = random.randint(*gas_ranges[scenario])

    # ── CO2 estimate from gas index (ppm) ─────────────────────
    co2_ppm = round(400 + (gas_index / 1023) * 1600, 1)

    # ── Temperature & Humidity (DHT22) ────────────────────────
    temperature = round(22 + 8 * math.sin(time_step / 20) +
                        random.uniform(-1, 1), 1)
    humidity    = round(55 - 0.3 * (temperature - 22) +
                        random.uniform(-3, 3), 1)
    humidity    = max(10, min(100, humidity))

    # ── AQI Calculation ───────────────────────────────────────
    aqi, category, aqi_color = calculate_aqi(pm25)

    return {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pm25":        pm25,
        "pm10":        pm10,
        "gas_index":   gas_index,
        "co2_ppm":     co2_ppm,
        "temperature": temperature,
        "humidity":    humidity,
        "aqi":         aqi,
        "category":    category,
        "aqi_color":   aqi_color,
        "scenario":    scenario,
    }


def check_alerts(data: dict) -> list:
    """
    Generates alert messages based on sensor thresholds.
    INTERVIEW TIP: "Threshold-based alerting is the core
                    logic in any environmental monitoring system."
    """
    alerts = []

    if data["pm25"] > 150:
        alerts.append(f"HAZARD: PM2.5 at {data['pm25']} ug/m3 — Stay indoors!")
    elif data["pm25"] > 55:
        alerts.append(f"WARNING: PM2.5 at {data['pm25']} ug/m3 — Wear a mask")
    elif data["pm25"] > 12:
        alerts.append(f"NOTICE: PM2.5 moderate at {data['pm25']} ug/m3")

    if data["co2_ppm"] > 1500:
        alerts.append(f"ALERT: High CO2 level {data['co2_ppm']} ppm — Ventilate!")
    elif data["co2_ppm"] > 1000:
        alerts.append(f"NOTICE: CO2 elevated at {data['co2_ppm']} ppm")

    if data["gas_index"] > 500:
        alerts.append(f"ALERT: Gas sensor high {data['gas_index']} — Possible leak!")

    if data["temperature"] > 38:
        alerts.append(f"WARNING: High temperature {data['temperature']}C")

    if data["humidity"] < 20:
        alerts.append(f"NOTICE: Low humidity {data['humidity']}% — Dry air")
    elif data["humidity"] > 85:
        alerts.append(f"NOTICE: High humidity {data['humidity']}% — Mold risk")

    return alerts