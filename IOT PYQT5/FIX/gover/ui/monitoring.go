// ui/monitoring.go
package ui

import (
	"sync"
	"time"
	"water-vending/api"
	   "water-vending/types"
    "water-vending/config"
	"water-vending/utils"

	"github.com/therecipe/qt/core"
)

// SensorData menyimpan data dari sensor
type SensorData struct {
	PH         float64 `json:"ph"`
	TDS        float64 `json:"tds"`
	WaterLevel float64 `json:"water_level"`
	Stale      bool    `json:"stale,omitempty"`
	Error      bool    `json:"error,omitempty"`
}

// SensorThread menangani monitoring sensor dalam goroutine terpisah
type SensorThread struct {
	core.QObject

	// Signals
	_ func(data SensorData) `signal:"sensorUpdated"`

	config           models.Config
	apiClient        *api.Client
	running          bool
	mutex            sync.Mutex
	logger           *utils.Logger
	lastSuccessfulData *SensorData
}

// NewSensorThread membuat instance baru SensorThread
func NewSensorThread(config models.Config) *SensorThread {
	return &SensorThread{
		QObject:    *core.NewQObject(nil),
		config:     config,
		apiClient:  api.NewClient(config.API),
		logger:     utils.GetLogger(),
	}
}

// Start memulai monitoring thread
func (s *SensorThread) Start() {
	s.mutex.Lock()
	s.running = true
	s.mutex.Unlock()

	go s.run()
}

// run adalah main loop untuk sensor monitoring
func (s *SensorThread) run() {
	for s.isRunning() {
		data, err := s.getSensorData()
		if err != nil {
			s.logger.Error("Error getting sensor data: %v", err)
			if s.lastSuccessfulData != nil {
				// Gunakan data terakhir yang berhasil dengan flag stale
				staleData := *s.lastSuccessfulData
				staleData.Stale = true
				s.SensorUpdated(staleData)
			} else {
				s.SensorUpdated(SensorData{Error: true})
			}
		} else {
			s.lastSuccessfulData = &data
			s.SensorUpdated(data)
			
			// Kirim data ke backend
			s.sendToBackend(data)
		}

		time.Sleep(time.Duration(s.config.App.UpdateInterval) * time.Second)
	}
}

// getSensorData mengambil data dari sensor ESP32
func (s *SensorThread) getSensorData() (SensorData, error) {
	// TODO: Implement actual ESP32 communication
	// Untuk sekarang kita return dummy data
	return SensorData{
		PH:         7.0,
		TDS:        150,
		WaterLevel: 80,
	}, nil
}

// sendToBackend mengirim data sensor ke backend
func (s *SensorThread) sendToBackend(data SensorData) {
	qualityData := map[string]float64{
		"tds_level":    data.TDS,
		"ph_level":     data.PH,
		"water_level":  data.WaterLevel,
	}

	if err := s.apiClient.RecordQuality(qualityData); err != nil {
		s.logger.Warning("Failed to send quality data to backend: %v", err)
	}
}

// Stop menghentikan monitoring thread
func (s *SensorThread) Stop() {
	s.mutex.Lock()
	s.running = false
	s.mutex.Unlock()
}

// isRunning memeriksa status thread
func (s *SensorThread) isRunning() bool {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	return s.running
}

// Cleanup membersihkan resources
func (s *SensorThread) Cleanup() {
	s.Stop()
}