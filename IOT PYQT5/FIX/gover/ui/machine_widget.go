// ui/machine_widget.go
package ui

import (
	"os"
	"water-vending/hardware"
	   "water-vending/types"
    "water-vending/config"
	"water-vending/utils"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
	"github.com/therecipe/qt/widgets"
)

// MachineWidget menangani tampilan dan kontrol mesin
type MachineWidget struct {
	widgets.QWidget

	// UI elements
	layout            *widgets.QVBoxLayout
	progressIndicator *widgets.QLabel
	progressBar       *widgets.QLabel
	machineImage      *widgets.QLabel
	startButton       *widgets.QPushButton

	// State
	selectedSize    string
	progress       int
	isFilling      bool
	progressSegments int

	// Controllers
	waterController *hardware.Controller
	logger         *utils.Logger

	// Signals
	_ func() `signal:"fillingCompleted"`
}

// NewMachineWidget membuat instance baru MachineWidget
func NewMachineWidget(config models.Config, parent widgets.QWidget_ITF) *MachineWidget {
	widget := &MachineWidget{
		QWidget:          *widgets.NewQWidget(parent, 0),
		progressSegments: 18,
		logger:          utils.GetLogger(),
		waterController: hardware.NewController(config.Hardware),
	}
	widget.init()
	return widget
}

// init menginisialisasi UI widget
func (m *MachineWidget) init() {
	m.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Fixed,
	)
	m.SetMinimumHeight(120)

	m.setupLayout()
}

// setupLayout mengatur layout widget
func (m *MachineWidget) setupLayout() {
	m.layout = widgets.NewQVBoxLayout()
	m.layout.SetSpacing(10)
	m.layout.SetContentsMargins(10, 10, 10, 10)
	m.SetLayout(m.layout)

	// Add progress container
	m.layout.AddWidget(m.createProgressContainer(), 0, 0)
	
	// Add machine display
	m.layout.AddWidget(m.createMachineDisplay(), 0, 0)
}

// createProgressContainer membuat container progress bar
func (m *MachineWidget) createProgressContainer() *widgets.QWidget {
	container := widgets.NewQWidget(nil, 0)
	container.SetStyleSheet(`
		background-color: #2C3E50;
		border-radius: 15px;
		padding: 10px;
	`)

	layout := widgets.NewQHBoxLayout()
	layout.SetContentsMargins(10, 5, 10, 5)
	container.SetLayout(layout)

	// Progress indicator
	m.progressIndicator = widgets.NewQLabel2("█", nil, 0)
	m.progressIndicator.SetStyleSheet(`
		color: #2ECC71;
		font-size: 24px;
	`)

	// Progress bar
	m.progressBar = widgets.NewQLabel2(m.getEmptyProgress(), nil, 0)
	m.progressBar.SetStyleSheet(`
		color: white;
		font-size: 16px;
	`)

	layout.AddWidget(m.progressIndicator, 0, 0)
	layout.AddWidget(m.progressBar, 1, 0)

	return container
}

// createMachineDisplay membuat display mesin
func (m *MachineWidget) createMachineDisplay() *widgets.QWidget {
	container := widgets.NewQWidget(nil, 0)
	container.SetStyleSheet(`
		background-color: #2C3E50;
		border-radius: 15px;
		padding: 10px;
	`)

	layout := widgets.NewQVBoxLayout()
	layout.SetSpacing(5)
	layout.SetContentsMargins(10, 5, 10, 5)
	container.SetLayout(layout)

	// Machine image
	m.machineImage = widgets.NewQLabel(nil, 0)
	m.machineImage.SetFixedSize2(80, 80)
	m.machineImage.SetAlignment(core.Qt__AlignCenter)
	m.machineImage.SetStyleSheet("background: transparent;")

	if _, err := os.Stat("5.png"); err == nil {
		pixmap := gui.NewQPixmap3("5.png")
		scaledMachine := pixmap.Scaled2(
			70, 70,
			core.Qt__KeepAspectRatio,
			core.Qt__SmoothTransformation,
		)
		m.machineImage.SetPixmap(scaledMachine)
	}

	// Start button
	m.startButton = widgets.NewQPushButton2("Start Filling", nil)
	m.startButton.SetFixedSize2(150, 40)
	m.startButton.SetEnabled(false)
	m.startButton.SetStyleSheet(`
		QPushButton {
			background-color: #2ECC71;
			border-radius: 20px;
			color: white;
			font-size: 16px;
			font-weight: bold;
			font-family: 'Segoe UI', Arial;
			border: none;
		}
		QPushButton:disabled {
			background-color: #95A5A6;
		}
		QPushButton:hover:!disabled {
			background-color: #27AE60;
		}
	`)

	m.startButton.ConnectClicked(func(checked bool) {
		m.startFillingAnimation()
	})

	layout.AddWidget(m.machineImage, 0, core.Qt__AlignCenter)
	layout.AddWidget(m.startButton, 0, core.Qt__AlignCenter)

	return container
}

// startFillingAnimation memulai proses pengisian air
func (m *MachineWidget) startFillingAnimation() {
	if !m.isFilling && m.selectedSize != "" {
		volume, ok := models.WaterVolumes[m.selectedSize]
		if !ok {
			m.logger.Error("Invalid size selected: %s", m.selectedSize)
			return
		}

		m.isFilling = true
		m.progress = 0
		m.startButton.SetEnabled(false)
		m.startButton.SetText("Filling...")
		m.progressIndicator.SetStyleSheet(`
			color: #E74C3C;
			font-size: 24px;
		`)

		// Start filling process in goroutine
		go m.startFilling(volume)
	}
}
// startFilling menjalankan proses pengisian
func (m *MachineWidget) startFilling(volume models.WaterVolume) {
    defer func() {
        // Pastikan motor berhenti dan filling selesai, bahkan jika terjadi error
        m.waterController.StopMotor()
        m.completeFilling()
    }()

    // Start motor
    if err := m.waterController.StartMotor(); err != nil {
        m.logger.Error("Failed to start motor: %v", err)
        return
    }

    targetPulses := volume.Pulses
    currentPulses := 0
    pulseChannel := make(chan struct{})

    // Setup flow sensor callback
    err := m.waterController.RegisterFlowCallback(func() {
        if m.isFilling {
            pulseChannel <- struct{}{}
        }
    })
    if err != nil {
        m.logger.Error("Failed to register flow callback: %v", err)
        return
    }

    // Timer untuk timeout
    timer := time.NewTimer(30 * time.Second)
    defer timer.Stop()

    // Channel untuk update progress setiap 100ms
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-pulseChannel:
            currentPulses++
            progress := int((float64(currentPulses) / float64(targetPulses)) * 100)
            if progress > 100 {
                progress = 100
            }
            
            // Update progress di UI thread
            core.QMetaObject_InvokeMethod2(m, "updateProgress", 
                core.Qt__QueuedConnection, 
                core.NewQVariant1(progress))

            if currentPulses >= targetPulses {
                m.logger.Info("Filling completed successfully")
                return
            }

        case <-ticker.C:
            // Jika dalam mode simulasi, increment progress
            if m.waterController.IsSimulated() {
                currentPulses += 5
                progress := int((float64(currentPulses) / float64(targetPulses)) * 100)
                if progress > 100 {
                    progress = 100
                }
                
                // Update progress di UI thread
                core.QMetaObject_InvokeMethod2(m, "updateProgress", 
                    core.Qt__QueuedConnection, 
                    core.NewQVariant1(progress))

                if currentPulses >= targetPulses {
                    m.logger.Info("Simulated filling completed")
                    return
                }
            }

        case <-timer.C:
            m.logger.Error("Filling timeout reached")
            return

        case <-m.ctx.Done():
            m.logger.Info("Filling cancelled")
            return
        }

        if !m.isFilling {
            m.logger.Info("Filling stopped by user")
            return
        }
    }
}

// updateProgress memperbarui tampilan progress
func (m *MachineWidget) updateProgress(progress int) {
	m.progress = progress
	filled := m.getFilledProgress(progress)
	m.progressBar.SetText(filled)
}

// getEmptyProgress mengembalikan string progress kosong
func (m *MachineWidget) getEmptyProgress() string {
	return strings.Repeat("▬", m.progressSegments)
}

// getFilledProgress mengembalikan string progress terisi
func (m *MachineWidget) getFilledProgress(progress int) string {
	filledCount := progress * m.progressSegments / 100
	filled := strings.Repeat("█", filledCount)
	empty := strings.Repeat("▬", m.progressSegments-filledCount)
	return filled + empty
}

// completeFilling menyelesaikan proses pengisian
func (m *MachineWidget) completeFilling() {
	m.isFilling = false
	m.startButton.SetEnabled(true)
	m.startButton.SetText("Start Filling")
	m.progressIndicator.SetStyleSheet(`
		color: #2ECC71;
		font-size: 24px;
	`)
	m.FillingCompleted()
}

// SetSelectedSize mengatur ukuran air yang dipilih
func (m *MachineWidget) SetSelectedSize(size string) {
	m.selectedSize = size
	m.startButton.SetEnabled(size != "")
}

// Cleanup membersihkan resources
func (m *MachineWidget) Cleanup() {
	if m.waterController != nil {
		m.waterController.Cleanup()
	}
}