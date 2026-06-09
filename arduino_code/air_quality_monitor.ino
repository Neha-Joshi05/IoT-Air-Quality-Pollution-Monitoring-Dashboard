// ============================================================
// air_quality_monitor.ino — ESP32 Firmware
// SIMULATE AT: https://wokwi.com
// ============================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHTPIN      4
#define DHTTYPE     DHT22
#define MQ135_PIN   34
#define BUZZER_PIN  26
#define LED_GREEN   14
#define LED_YELLOW  27
#define LED_RED     25

const char* WIFI_SSID   = "YOUR_WIFI_SSID";
const char* WIFI_PASS   = "YOUR_WIFI_PASS";
const char* MQTT_SERVER = "broker.hivemq.com";

DHT          dht(DHTPIN, DHTTYPE);
WiFiClient   espClient;
PubSubClient mqtt(espClient);

// AQI thresholds for PM2.5 via MQ135 proxy
void setAQIIndicator(int gasVal) {
  digitalWrite(LED_GREEN,  LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED,    LOW);
  digitalWrite(BUZZER_PIN, LOW);

  if (gasVal < 150) {
    digitalWrite(LED_GREEN, HIGH);       // Good
  } else if (gasVal < 300) {
    digitalWrite(LED_YELLOW, HIGH);      // Moderate
  } else if (gasVal < 500) {
    digitalWrite(LED_RED, HIGH);         // Unhealthy
  } else {
    digitalWrite(LED_RED, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);      // Hazardous — buzzer ON
  }
}

void reconnectMQTT() {
  while (!mqtt.connected()) {
    if (mqtt.connect("AirQualityNode_001"))
      Serial.println("MQTT Connected");
    else
      delay(3000);
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_GREEN,  OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED,    OUTPUT);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi Connected");

  mqtt.setServer(MQTT_SERVER, 1883);
}

void loop() {
  if (!mqtt.connected()) reconnectMQTT();
  mqtt.loop();

  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  int   gas  = analogRead(MQ135_PIN);

  if (isnan(temp) || isnan(hum)) {
    temp = 25.0; hum = 60.0;
  }

  // Classify air quality
  String category;
  if      (gas < 150) category = "Good";
  else if (gas < 300) category = "Moderate";
  else if (gas < 500) category = "Unhealthy";
  else                category = "Hazardous";

  // Build JSON payload
  char payload[300];
  snprintf(payload, sizeof(payload),
    "{\"temp\":%.1f,\"hum\":%.1f,\"gas\":%d,\"category\":\"%s\"}",
    temp, hum, gas, category.c_str()
  );

  mqtt.publish("airquality/node1/data", payload);
  setAQIIndicator(gas);

  Serial.printf("Temp:%.1fC | Hum:%.1f%% | Gas:%d | %s\n",
    temp, hum, gas, category.c_str());

  delay(5000);
}