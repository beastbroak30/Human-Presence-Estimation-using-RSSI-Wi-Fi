#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "ESP32test";
const char* password = "123456789";

// Assign static IP for this ESP8266 device
IPAddress local_IP(192, 168, 1, 9);  // Change for each ESP8266: 6, 7, 8, or 9
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// Create web server on port 80
ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);

  WiFi.config(local_IP, gateway, subnet);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Set up /rssi endpoint
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
