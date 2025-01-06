// types/types.go
package types

// WaterVolume mendefinisikan struktur untuk volume air
type WaterVolume struct {
    Name        string
    Pulses      int
    DisplayName string
    Price       string
}

// APIConfig mendefinisikan konfigurasi API
type APIConfig struct {
    BaseURL       string `json:"base_url"`
    MachineID     string `json:"machine_id"`
    Timeout       int    `json:"timeout"`
    RetryAttempts int    `json:"retry_attempts"`
    RetryDelay    int    `json:"retry_delay"`
}

// HardwareConfig mendefinisikan konfigurasi hardware
type HardwareConfig struct {
    FlowSensorPin int    `json:"flow_sensor_pin"`
    MotorPin      int    `json:"motor_pin"`
    ESP32IP       string `json:"esp32_ip"`
    ESP32Port     int    `json:"esp32_port"`
}

// AppConfig mendefinisikan konfigurasi aplikasi
type AppConfig struct {
    VideoPath      string `json:"video_path"`
    LogFile        string `json:"log_file"`
    LogLevel       string `json:"log_level"`
    UpdateInterval int    `json:"update_interval"`
}

// Config adalah struktur utama konfigurasi
type Config struct {
    API      APIConfig      `json:"api"`
    Hardware HardwareConfig `json:"hardware"`
    App      AppConfig      `json:"app"`
}

// Constants untuk volume air
var WaterVolumes = map[string]WaterVolume{
    "100 ml": {
        Name:        "100 ml",
        Pulses:      108,
        DisplayName: "100 ml",
        Price:       "Rp. 3.000",
    },
    "350 ml": {
        Name:        "350 ml",
        Pulses:      378,
        DisplayName: "350 ml",
        Price:       "Rp. 5.000",
    },
    "600 ml": {
        Name:        "600 ml",
        Pulses:      670,
        DisplayName: "600 ml",
        Price:       "Rp. 7.000",
    },
    "1 Liter": {
        Name:        "1 Liter",
        Pulses:      1080,
        DisplayName: "1 Liter",
        Price:       "Rp. 15.000",
    },
}