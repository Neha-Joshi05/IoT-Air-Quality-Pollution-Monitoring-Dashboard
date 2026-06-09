# ============================================================
# main.py — Terminal Simulation Runner
# HOW TO RUN: python main.py
# ============================================================

import time
from python_simulation.sensor_simulator import generate_sensor_data, check_alerts
from python_simulation.data_logger import init_logger, log_reading


def main():
    print("\n" + "=" * 60)
    print("   IoT Air Quality & Pollution Monitoring System")
    print("   Simulation running... Press CTRL+C to stop")
    print("=" * 60 + "\n")

    init_logger()
    step = 0

    try:
        while True:
            step += 1
            data   = generate_sensor_data(step)
            alerts = check_alerts(data)
            log_reading(data, alerts)

            # AQI color indicator in terminal
            aqi_bar = {
                "Good":             "[GOOD]     ",
                "Moderate":         "[MODERATE] ",
                "Unhealthy for Sensitive": "[SENSITIVE]",
                "Unhealthy":        "[UNHEALTHY]",
                "Very Unhealthy":   "[V.UNHLTHY]",
                "Hazardous":        "[HAZARDOUS]",
            }.get(data["category"], "[UNKNOWN]  ")

            print(f"[{step:04d}] {data['timestamp']}")
            print(f"  AQI: {data['aqi']:3d} {aqi_bar} | "
                  f"PM2.5: {data['pm25']:6.1f} ug/m3 | "
                  f"PM10: {data['pm10']:6.1f} ug/m3")
            print(f"  CO2: {data['co2_ppm']:6.1f} ppm | "
                  f"Gas: {data['gas_index']:4d} | "
                  f"Temp: {data['temperature']}C | "
                  f"Hum: {data['humidity']}%")

            if alerts:
                for a in alerts:
                    print(f"  >> {a}")
            else:
                print(f"  >> All parameters normal")
            print()

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped. Data saved to data/air_quality_log.csv")


if __name__ == "__main__":
    main()