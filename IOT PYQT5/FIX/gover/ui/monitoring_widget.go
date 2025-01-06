// ui/monitoring_widget.go
package ui

import (
	   "water-vending/types"
    "water-vending/config"
	"water-vending/utils"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/widgets"
)

// MonitoringWidget menampilkan informasi kualitas air
type MonitoringWidget struct {
	widgets.QWidget

	config       models.Config
	logger       *utils.Logger
	sensorThread *SensorThread

	// UI elements
	layout           *widgets.QVBoxLayout
	monitorContainer *widgets.QWidget
	phWidget         *widgets.QWidget
	tdsWidget        *widgets.QWidget
	phValue          *widgets.QLabel
	tdsValue         *widgets.QLabel
}

// NewMonitoringWidget membuat instance baru MonitoringWidget
func NewMonitoringWidget(config models.Config, parent widgets.QWidget_ITF) *MonitoringWidget {
	widget := &MonitoringWidget{
		QWidget: *widgets.NewQWidget(parent, 0),
		config:  config,
		logger:  utils.GetLogger(),
	}
	widget.init()
	return widget
}

// init menginisialisasi UI widget
func (m *MonitoringWidget) init() {
	// Set size policy
	m.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Fixed,
	)
	m.SetMinimumHeight(150)

	// Setup layout utama
	m.setupUI()

	// Setup sensor thread
	m.setupSensorThread()
}

// setupUI membuat dan mengatur UI elements
func (m *MonitoringWidget) setupUI() {
	m.layout = widgets.NewQVBoxLayout()
	m.layout.SetSpacing(8)
	m.layout.SetContentsMargins(8, 8, 8, 8)
	m.SetLayout(m.layout)

	// Title
	title := widgets.NewQLabel2("Water Quality Monitoring", nil, 0)
	title.SetStyleSheet(`
		font-size: 18px;
		font-weight: bold;
		color: #2C3E50;
		font-family: 'Segoe UI', Arial;
	`)
	title.SetAlignment(core.Qt__AlignCenter)

	// Monitor container
	m.monitorContainer = widgets.NewQWidget(nil, 0)
	m.monitorContainer.SetStyleSheet(`
		QWidget {
			background-color: #F8F9FA;
			border-radius: 15px;
			border: 2px solid #E9ECEF;
			padding: 10px;
		}
	`)

	monitorLayout := widgets.NewQHBoxLayout()
	monitorLayout.SetContentsMargins(8, 4, 8, 4)
	m.monitorContainer.SetLayout(monitorLayout)

	// Create monitoring displays
	m.phWidget = m.createMonitorDisplay("pH Value")
	m.tdsWidget = m.createMonitorDisplay("TDS Value")

	monitorLayout.AddWidget(m.phWidget, 0, 0)
	monitorLayout.AddWidget(m.tdsWidget, 0, 0)

	// Add widgets to main layout
	m.layout.AddWidget(title, 0, 0)
	m.layout.AddWidget(m.monitorContainer, 0, 0)
}

// createMonitorDisplay membuat display untuk nilai monitoring
func (m *MonitoringWidget) createMonitorDisplay(title string) *widgets.QWidget {
	widget := widgets.NewQWidget(nil, 0)
	layout := widgets.NewQVBoxLayout()
	layout.SetSpacing(4)
	widget.SetLayout(layout)

	// Title label
	titleLabel := widgets.NewQLabel2(title, nil, 0)
	titleLabel.SetStyleSheet(`
		font-size: 14px;
		font-weight: bold;
		color: #2C3E50;
		padding: 2px;
	`)
	titleLabel.SetAlignment(core.Qt__AlignCenter)

	// Value label
	valueLabel := widgets.NewQLabel2("Not Connected", nil, 0)
	valueLabel.SetStyleSheet(`
		background-color: white;
		padding: 8px;
		border-radius: 8px;
		font-size: 14px;
		font-weight: bold;
		border: 1px solid #E9ECEF;
	`)
	valueLabel.SetAlignment(core.Qt__AlignCenter)
	valueLabel.SetWordWrap(true)

	layout.AddWidget(titleLabel, 0, 0)
	layout.AddWidget(valueLabel, 0, 0)

	// Store value label reference
	if title == "pH Value" {
		m.phValue = valueLabel
	} else {
		m.tdsValue = valueLabel
	}

	return widget
}

// setupSensorThread inisialisasi dan menjalankan sensor thread
func (m *MonitoringWidget) setupSensorThread() {
	m.sensorThread = NewSensorThread(m.config)
	
	// Connect signal untuk update sensor
	m.sensorThread.ConnectSensorUpdated(func(data SensorData) {
		m.updateSensorDisplay(data)
	})

	// Start sensor thread
	m.sensorThread.Start()
}

// updateSensorDisplay memperbarui display dengan data sensor
func (m *MonitoringWidget) updateSensorDisplay(data SensorData) {
	if data.Error {
		m.phValue.SetText("Not Connected")
		m.tdsValue.SetText("Not Connected")
		return
	}

	// Update pH value
	if data.Stale {
		m.phValue.SetStyleSheet(`
			background-color: #FFF3CD;
			padding: 8px;
			border-radius: 8px;
			font-size: 14px;
			font-weight: bold;
			border: 1px solid #FFE69C;
		`)
	} else {
		m.phValue.SetStyleSheet(`
			background-color: white;
			padding: 8px;
			border-radius: 8px;
			font-size: 14px;
			font-weight: bold;
			border: 1px solid #E9ECEF;
		`)
	}
	m.phValue.SetText(core.NewQString5(1, 'f', 2).Arg(data.PH))

	// Update TDS value
	if data.Stale {
		m.tdsValue.SetStyleSheet(`
			background-color: #FFF3CD;
			padding: 8px;
			border-radius: 8px;
			font-size: 14px;
			font-weight: bold;
			border: 1px solid #FFE69C;
		`)
	} else {
		m.tdsValue.SetStyleSheet(`
			background-color: white;
			padding: 8px;
			border-radius: 8px;
			font-size: 14px;
			font-weight: bold;
			border: 1px solid #E9ECEF;
		`)
	}
	m.tdsValue.SetText(core.NewQString5(0, 'f', 0).Arg(data.TDS))
}

// Cleanup membersihkan resources
func (m *MonitoringWidget) Cleanup() {
	if m.sensorThread != nil {
		m.sensorThread.Cleanup()
	}
}