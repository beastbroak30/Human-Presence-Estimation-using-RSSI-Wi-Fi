#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const char* ssid = "ESP32test";
const char* password = "123456789";

IPAddress local_IP(192, 168, 1, 5);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

IPAddress sensorIPs[] = {
  IPAddress(192, 168, 1, 6),
  IPAddress(192, 168, 1, 7),
  IPAddress(192, 168, 1, 8),
  IPAddress(192, 168, 1, 9)
};

int32_t rssiValues[4] = {0};
unsigned long startTime;
bool startedRSSI = false;

void setup() {
  Serial.begin(115200);
  Wire.begin(5, 4);

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR, false, false)) {
    Serial.println("OLED failed");
    while (1);
  }

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("WiFi Connected!");
  display.display();
  delay(500);

  checkDevices();
  startTime = millis();
}

void loop() {
  if (!startedRSSI && millis() - startTime > 10000) {
    startedRSSI = true;
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("RSSI Monitor:");
    display.display();
  }

  if (startedRSSI) {
    fetchRSSI();
    delay(10);
  }
}

void checkDevices() {
  display.clearDisplay();
  for (int i = 0; i < 4; i++) {
    WiFiClient client;
    bool isOnline = client.connect(sensorIPs[i], 80);
    client.stop();

    display.setCursor(0, i * 12);
    display.printf("ESP%d: %s", i + 1, isOnline ? "OK" : "NO");
    display.display();
    delay(300);
  }
}

void fetchRSSI() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("RSSI Values:");

  String line = "";

  for (int i = 0; i < 4; i++) {
    HTTPClient http;
    String url = "http://" + sensorIPs[i].toString() + "/rssi";
    http.begin(url);
    int httpCode = http.GET();
    String payload = httpCode == 200 ? http.getString() : "0";

    rssiValues[i] = payload.toInt();
    display.setCursor(0, 12 + i * 12);
    display.printf("ESP%d: %s", i + 1, payload.c_str());
    display.display();
    http.end();

    line += String(rssiValues[i]);
    if (i != 3) line += ",";
  }

  Serial.println(line);
}
