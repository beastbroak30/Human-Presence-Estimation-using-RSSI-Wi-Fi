#include <WiFi.h>         // Use <ESP8266WiFi.h> instead for ESP8266
#include <WebServer.h>    // Use <ESP8266WebServer.h> for ESP8266

const char* ssid = "ESP32test";
const char* password = "123456789";

// Assign each device a unique static IP
IPAddress local_IP(192, 168, 1, 7);  // Change to 7, 8, or 9 for others
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

WebServer server(80);  // Use ESP8266WebServer for ESP8266

void setup() {
  Serial.begin(115200);

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Route to return RSSI
  server.on("/rssi", []() {
    int32_t rssi = WiFi.RSSI();
    server.send(200, "text/plain", String(rssi));
    Serial.println("RSSI requested: " + String(rssi));
  });

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
