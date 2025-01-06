#include <WiFi.h>
#include <WebServer.h>

// WiFi Credentials
const char* ssid = "haisayakaka";     // Ganti dengan nama WiFi Anda
const char* password = "akujomok";  // Ganti dengan password WiFi Anda

// Web Server pada port 80
WebServer server(80);

// Konfigurasi Pin dan Konstanta
const int PH_PIN = 36;         // GPIO36 (VP) untuk input analog
const int SAMPLES = 10;        // Jumlah sampel untuk average reading
const float VOLTAGE_REF = 3.3 - 0.1; // Referensi voltage ESP32

// Variabel Kalibrasi pH
const float PH7_VOLTAGE = 2.5; // Voltage pada pH 7 (perlu dikalibrasi)
const float PH4_VOLTAGE = 3.0; // Voltage pada pH 4 (perlu dikalibrasi)
const float VOLTAGE_PER_PH = (PH4_VOLTAGE - PH7_VOLTAGE) / 3; // Voltage per unit pH

// Variabel untuk pembacaan
float avgVoltage = 0.0;
float phValue = 0.0;
String phStatus = "";

// HTML webpage template
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML>
<html>
<head>
  <title>ESP32 pH Sensor Monitor</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; margin: 0px auto; padding: 15px; }
    .reading { font-size: 2.8rem; }
    .card { background-color: white; box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.1);
            border-radius: 10px; padding: 15px; margin: 20px; }
    .status { font-size: 1.2rem; margin: 10px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>ESP32 pH Sensor Monitor</h2>
    <div class="reading">pH: <span id="ph">%PH_VALUE%</span></div>
    <div class="status">Status: <span id="status">%PH_STATUS%</span></div>
    <div class="status">Voltage: <span id="voltage">%VOLTAGE%</span> V</div>
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
          document.getElementById("ph").innerHTML = data.ph;
          document.getElementById("status").innerHTML = data.status;
          document.getElementById("voltage").innerHTML = data.voltage;
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
  // Inisialisasi Serial
  Serial.begin(115200);
  
  // Konfigurasi ADC
  analogSetWidth(12);          // Set ADC ke 12-bit (0-4095)
  analogSetAttenuation(ADC_11db); // Set attenuation untuk range 0-3.3V
  
  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  Serial.println("\nMenghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi terhubung!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Setup route handler untuk web server
  server.on("/", handleRoot);
  server.on("/data", handleData);
  
  // Mulai web server
  server.begin();
  Serial.println("Web server aktif");
   Serial.println(WiFi.localIP());

  // Tunggu sensor stabil
  delay(2000);
}

// Fungsi untuk membaca dan memfilter nilai analog (tidak berubah)
float readPHVoltage() {
  float voltage = 0.0;
  int samples[SAMPLES];
  
  for(int i = 0; i < SAMPLES; i++) {
    samples[i] = analogRead(PH_PIN);
    delay(10);
  }
  
  for(int i = 0; i < SAMPLES-1; i++) {
    for(int j = i+1; j < SAMPLES; j++) {
      if(samples[i] > samples[j]) {
        int temp = samples[i];
        samples[i] = samples[j];
        samples[j] = temp;
      }
    }
  }
  
  int validSamples = SAMPLES - 4;
  float avgValue = 0;
  for(int i = 2; i < SAMPLES-2; i++) {
    avgValue += samples[i];
  }
  
  voltage = (avgValue / validSamples) * (VOLTAGE_REF / 4095.0);
  return voltage;
}

// Fungsi untuk mengkonversi voltage ke nilai pH (tidak berubah)
float voltageToPH(float voltage) {
  return 7.0 + ((PH7_VOLTAGE - voltage) / VOLTAGE_PER_PH);
}

// Handler untuk halaman utama
void handleRoot() {
  String html = String(index_html);
  html.replace("%PH_VALUE%", String(phValue, 2));
  html.replace("%PH_STATUS%", phStatus);
  html.replace("%VOLTAGE%", String(avgVoltage, 3));
  server.sendHeader("Access-Control-Allow-Origin", "*");
        server.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
        server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
    
  server.send(200, "text/html", html);
}

// Handler untuk data JSON
void handleData() {
  String json = "{";
  json += "\"ph\":\"" + String(phValue, 2) + "\",";
  json += "\"status\":\"" + phStatus + "\",";
  json += "\"voltage\":\"" + String(avgVoltage, 3) + "\"";
  json += "}";
  server.send(200, "application/json", json);
}

void loop() {
  // Handle client requests
  server.handleClient();
  
  // Baca voltage dengan filter
  avgVoltage = readPHVoltage();
  
  // Konversi ke pH
  phValue = voltageToPH(avgVoltage);
  
  // Update status pH
  if (phValue < 0 || phValue > 14) {
    phStatus = "Error: Pembacaan tidak valid";
  } else if(phValue < 6.5) {
    phStatus = "Asam";
  } else if(phValue > 7.5) {
    phStatus = "Basa";
  } else {
    phStatus = "Netral";
  }
  
  
  delay(500); // Delay antara pembacaan
}