#include <WiFi.h>
#include <WebServer.h>
#include <EEPROM.h>
#include "GravityTDS.h"

// WiFi Credentials
const char* ssid = "haisayakaka";     // Replace with your WiFi name
const char* password = "akujomok";     // Replace with your WiFi password

// Web Server on port 80
WebServer server(80);

// TDS Sensor Configuration
#define TdsSensorPin 25
#define EEPROM_SIZE 512
GravityTDS gravityTds;
float temperature = 25, tdsValue;

// HTML webpage template
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML>
<html>
<head>
  <title>ESP32 TDS Sensor Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; margin: 0px auto; padding: 15px; }
    .reading { font-size: 2.8rem; }
    .card { background-color: white; box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.1);
            border-radius: 10px; padding: 15px; margin: 20px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>ESP32 TDS Sensor Monitor</h2>
    <div class="reading">TDS Value: <span id="tds">%TDS_VALUE%</span> ppm</div>
    <div class="reading">Temperature: <span id="temp">%TEMPERATURE%</span> °C</div>
  </div>
  <script>
    setInterval(function() {
      getData();
    }, 2000);
    
    function getData() {
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          var data = JSON.parse(this.responseText);
          document.getElementById("tds").innerHTML = data.tds;
          document.getElementById("temp").innerHTML = data.temperature;
        }
      };
      xhttp.open("GET", "/data", true);
      xhttp.send();
    }
  </script>
</body>
</html>
)rawliteral";

void setup() {
    Serial.begin(115200);
    
    // Initialize EEPROM
    EEPROM.begin(EEPROM_SIZE);
    
    // Initialize TDS Sensor
    gravityTds.setPin(TdsSensorPin);
    gravityTds.setAref(3.3);
    gravityTds.setAdcRange(4096);
    gravityTds.begin();
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Setup route handlers
    server.on("/", handleRoot);
    server.on("/data", handleData);
    
    // Start web server
    server.begin();
    Serial.println("Web server active");
}

void handleRoot() {
    String html = String(index_html);
    html.replace("%TDS_VALUE%", String(tdsValue, 0));
    html.replace("%TEMPERATURE%", String(temperature, 1));
    server.send(200, "text/html", html);
}

void handleData() {
    String json = "{";
    json += "\"tds\":\"" + String(tdsValue, 0) + "\",";
    json += "\"temperature\":\"" + String(temperature, 1) + "\"";
    json += "}";
    server.send(200, "application/json", json);
}

void loop() {
    // Handle web client requests
    server.handleClient();
    
    // Update TDS reading
    gravityTds.setTemperature(temperature);
    gravityTds.update();
    tdsValue = gravityTds.getTdsValue();
    
    // Print to Serial for debugging
    Serial.print(tdsValue, 0);
    Serial.println(" ppm");
    
    delay(1000);
}