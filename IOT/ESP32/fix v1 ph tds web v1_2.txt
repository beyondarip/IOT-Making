#include <WiFi.h>
#include <WebServer.h>

// WiFi Credentials
const char* ssid = "haisayakaka";     
const char* password = "akujomok";  

// Web Server pada port 80
WebServer server(80);

// Pin Configuration
const int PH_PIN = 36;         // GPIO36 untuk pH
const int TDS_PIN = 39;        // GPIO39 untuk TDS

// Sampling Configuration
const int SAMPLES = 10;        
const float VOLTAGE_REF = 3.3 - 0.1; 

// pH Calibration
const float PH7_VOLTAGE = 2.5; 
const float PH4_VOLTAGE = 3.0; 
const float VOLTAGE_PER_PH = (PH4_VOLTAGE - PH7_VOLTAGE) / 3;

// TDS Configuration
const int SCOUNT = 30;       
int analogBuffer[SCOUNT];    
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0;
float temperature = 25;      

// Variables for readings
float avgVoltagePH = 0.0;
float phValue = 0.0;
String phStatus = "";
float tdsValue = 0.0;
float tdsVoltage = 0.0;

// HTML webpage template
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML>
<html>
<head>
  <title>ESP32 pH & TDS Monitor</title>
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
    <h2>pH Sensor Monitor</h2>
    <div class="reading">pH: <span id="ph">%PH_VALUE%</span></div>
    <div class="status">Status: <span id="status">%PH_STATUS%</span></div>
    <div class="status">Voltage: <span id="voltage">%VOLTAGE%</span> V</div>
  </div>
  
  <div class="card">
    <h2>TDS Sensor Monitor</h2>
    <div class="reading">TDS: <span id="tds">%TDS_VALUE%</span> ppm</div>
    <div class="status">Voltage: <span id="tdsVoltage">%TDS_VOLTAGE%</span> V</div>
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
          document.getElementById("status").innerHTML = data.phStatus;
          document.getElementById("voltage").innerHTML = data.phVoltage;
          document.getElementById("tds").innerHTML = data.tds;
          document.getElementById("tdsVoltage").innerHTML = data.tdsVoltage;
        }
      };
      xhttp.open("GET", "/data", true);
      xhttp.send();
    }
  </script>
</body>
</html>
)rawliteral";

// TDS Functions
int getMedianNum(int bArray[], int iFilterLen) {
  int bTab[iFilterLen];
  for (byte i = 0; i < iFilterLen; i++)
    bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}

void readTDS() {
  static unsigned long analogSampleTimepoint = millis();
  
  if (millis() - analogSampleTimepoint > 40U) {
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TDS_PIN);    
    analogBufferIndex++;
    if(analogBufferIndex == SCOUNT) 
      analogBufferIndex = 0;
  }
  
  static unsigned long printTimepoint = millis();
  if (millis() - printTimepoint > 800U) {
    printTimepoint = millis();
    for(int copyIndex = 0; copyIndex < SCOUNT; copyIndex++)
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
    
    int medianValue = getMedianNum(analogBufferTemp, SCOUNT);
    tdsVoltage = medianValue * (float)VOLTAGE_REF / 4096.0;
    
    float compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0);
    float compensationVoltage = tdsVoltage / compensationCoefficient;
    
    tdsValue = (133.42 * pow(compensationVoltage, 3) - 255.86 * pow(compensationVoltage, 2) + 857.39 * compensationVoltage) * 0.5;
  }
}

// pH Functions
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

float voltageToPH(float voltage) {
  return 7.0 + ((PH7_VOLTAGE - voltage) / VOLTAGE_PER_PH);
}

void setup() {
  Serial.begin(115200);
  
  analogSetWidth(12);          
  analogSetAttenuation(ADC_11db);
  
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

  server.on("/", handleRoot);
  server.on("/data", handleData);
  
  server.begin();
  Serial.println("Web server aktif");
  Serial.println(WiFi.localIP());

  delay(2000);
}

void handleRoot() {
  String html = String(index_html);
  html.replace("%PH_VALUE%", String(phValue, 2));
  html.replace("%PH_STATUS%", phStatus);
  html.replace("%VOLTAGE%", String(avgVoltagePH, 3));
  html.replace("%TDS_VALUE%", String(tdsValue, 0));
  html.replace("%TDS_VOLTAGE%", String(tdsVoltage, 3));
  
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "text/html", html);
}

void handleData() {
  String json = "{";
  json += "\"ph\":\"" + String(phValue, 2) + "\",";
  json += "\"phStatus\":\"" + phStatus + "\",";
  json += "\"phVoltage\":\"" + String(avgVoltagePH, 3) + "\",";
  json += "\"tds\":\"" + String(tdsValue, 0) + "\",";
  json += "\"tdsVoltage\":\"" + String(tdsVoltage, 3) + "\"";
  json += "}";
  server.send(200, "application/json", json);
}

void loop() {
  server.handleClient();
  
  // Read pH
  avgVoltagePH = readPHVoltage();
  phValue = voltageToPH(avgVoltagePH);
  
  if (phValue < 0 || phValue > 14) {
    phStatus = "Error: Pembacaan tidak valid";
  } else if(phValue < 6.5) {
    phStatus = "Asam";
  } else if(phValue > 7.5) {
    phStatus = "Basa";
  } else {
    phStatus = "Netral";
  }

  // Read TDS
  readTDS();
  
  delay(100);
}