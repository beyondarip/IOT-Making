// config/manager.go
package config

import (
    "encoding/json"
    "io/ioutil"
    "log"
    "os"
    "sync"
    "water-vending/types"
)

// Manager mengelola konfigurasi aplikasi dengan singleton pattern
type Manager struct {
    config     *types.Config
    configPath string
    mu         sync.RWMutex
}

var (
    instance *Manager
    once     sync.Once
)

// GetInstance mengembalikan instance singleton dari Manager
func GetInstance() *Manager {
    once.Do(func() {
        instance = &Manager{
            configPath: "config.json",
        }
        instance.LoadConfig()
    })
    return instance
}

// LoadConfig memuat konfigurasi dari file JSON
func (m *Manager) LoadConfig() error {
    m.mu.Lock()
    defer m.mu.Unlock()

    if _, err := os.Stat(m.configPath); os.IsNotExist(err) {
        if err := m.createDefaultConfig(); err != nil {
            return err
        }
    }

    data, err := ioutil.ReadFile(m.configPath)
    if err != nil {
        return err
    }

    config := &types.Config{}
    if err := json.Unmarshal(data, config); err != nil {
        return err
    }

    m.config = config
    return nil
}

// createDefaultConfig membuat file konfigurasi default
func (m *Manager) createDefaultConfig() error {
    defaultConfig := &types.Config{
        API: types.APIConfig{
            BaseURL:       "http://localhost:8000",
            MachineID:     "VM001",
            Timeout:       5,
            RetryAttempts: 3,
            RetryDelay:    1,
        },
        Hardware: types.HardwareConfig{
            FlowSensorPin: 20,
            MotorPin:      21,
            ESP32IP:       "192.168.137.82",
            ESP32Port:     80,
        },
        App: types.AppConfig{
            VideoPath:      "yqq.mkv",
            LogFile:        "vending_machine.log",
            LogLevel:       "INFO",
            UpdateInterval: 2,
        },
    }

    data, err := json.MarshalIndent(defaultConfig, "", "    ")
    if err != nil {
        return err
    }

    if err := ioutil.WriteFile(m.configPath, data, 0644); err != nil {
        return err
    }

    m.config = defaultConfig
    return nil
}

// GetConfig mengembalikan salinan konfigurasi saat ini
func (m *Manager) GetConfig() types.Config {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return *m.config
}

// SaveConfig menyimpan konfigurasi ke file
func (m *Manager) SaveConfig() error {
    m.mu.RLock()
    defer m.mu.RUnlock()

    data, err := json.MarshalIndent(m.config, "", "    ")
    if err != nil {
        return err
    }

    return ioutil.WriteFile(m.configPath, data, 0644)
}