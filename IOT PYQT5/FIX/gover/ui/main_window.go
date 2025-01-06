// ui/main_window.go
package ui

import (
	   "water-vending/types"
    "water-vending/config"
	"water-vending/utils"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
	"github.com/therecipe/qt/widgets"
)

// MainWindow adalah window utama aplikasi
type MainWindow struct {
	widgets.QMainWindow

	// Configuration
	config models.Config
	logger *utils.Logger

	// UI Components
	centralWidget    *widgets.QWidget
	mainLayout      *widgets.QVBoxLayout
	contentLayout   *widgets.QHBoxLayout
	leftPanel       *widgets.QWidget
	rightPanel      *widgets.QWidget
	videoLabel      *widgets.QLabel
	videoThread     *VideoThread
	monitoringWidget *MonitoringWidget
	machineWidget   *MachineWidget
	sizeButtons     []*WaterButton

	// Cleanup handlers
	cleanupHandlers []interface{ Cleanup() }
}

// NewMainWindow membuat instance baru MainWindow
func NewMainWindow(config models.Config) *MainWindow {
	window := &MainWindow{
		QMainWindow: *widgets.NewQMainWindow(nil, 0),
		config:     config,
		logger:     utils.GetLogger(),
	}
	window.init()
	return window
}

// init menginisialisasi UI
func (m *MainWindow) init() {
	m.SetWindowTitle("Innovative Aqua Solution")
	m.SetStyleSheet("background-color: #E3F2FD;")

	// Set ukuran window
	screen := widgets.QApplication_Desktop().ScreenGeometry(0)
	width := int(float64(screen.Width()) * 0.8)
	height := int(float64(screen.Height()) * 0.8)
	m.SetMinimumSize2(1366, 768)
	m.Resize2(width, height)

	// Setup central widget
	m.centralWidget = widgets.NewQWidget(nil, 0)
	m.SetCentralWidget(m.centralWidget)
	m.mainLayout = widgets.NewQVBoxLayout()
	m.mainLayout.SetContentsMargins(20, 20, 20, 20)
	m.mainLayout.SetSpacing(20)
	m.centralWidget.SetLayout(m.mainLayout)

	// Setup content
	content := widgets.NewQWidget(nil, 0)
	content.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Expanding,
	)
	m.contentLayout = widgets.NewQHBoxLayout()
	m.contentLayout.SetSpacing(20)
	content.SetLayout(m.contentLayout)

	// Setup panels
	m.setupLeftPanel()
	m.setupRightPanel()

	m.contentLayout.AddWidget(m.leftPanel, 7, 0)
	m.contentLayout.AddWidget(m.rightPanel, 0, 0)
	m.mainLayout.AddWidget(content, 0, 0)

	// Setup video
	m.setupVideo()
}

// setupLeftPanel mengatur panel kiri
func (m *MainWindow) setupLeftPanel() {
	m.leftPanel = widgets.NewQWidget(nil, 0)
	m.leftPanel.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Expanding,
	)
	leftLayout := widgets.NewQVBoxLayout()
	leftLayout.SetSpacing(20)
	m.leftPanel.SetLayout(leftLayout)

	// Add video container
	videoContainer := m.createVideoContainer()
	leftLayout.AddWidget(videoContainer, 7, 0)

	// Add monitoring widget
	m.monitoringWidget = NewMonitoringWidget(m.config, nil)
	leftLayout.AddWidget(m.monitoringWidget, 3, 0)
	m.registerCleanup(m.monitoringWidget)
}

// createVideoContainer membuat container untuk video
func (m *MainWindow) createVideoContainer() *widgets.QWidget {
	container := widgets.NewQWidget(nil, 0)
	container.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Expanding,
	)
	container.SetStyleSheet(`
		background-color: #F8F9FA;
		border-radius: 20px;
		border: 2px solid #E9ECEF;
		padding: 10px;
	`)

	layout := widgets.NewQVBoxLayout()
	container.SetLayout(layout)

	m.videoLabel = widgets.NewQLabel(nil, 0)
	m.videoLabel.SetSizePolicy2(
		widgets.QSizePolicy__Expanding,
		widgets.QSizePolicy__Expanding,
	)
	m.videoLabel.SetMinimumSize2(640, 480)
	m.videoLabel.SetMaximumSize2(1280, 720)
	m.videoLabel.SetAlignment(core.Qt__AlignCenter)
	m.videoLabel.SetStyleSheet(`
		QLabel {
			background-color: #E9ECEF;
			border-radius: 10px;
		}
	`)

	layout.AddWidget(m.videoLabel, 0, 0)
	return container
}

// setupRightPanel mengatur panel kanan
func (m *MainWindow) setupRightPanel() {
	m.rightPanel = widgets.NewQWidget(nil, 0)
	m.rightPanel.SetFixedWidth(350)
	rightLayout := widgets.NewQVBoxLayout()
	rightLayout.SetSpacing(20)
	m.rightPanel.SetLayout(rightLayout)

	// Add water selection section
	selectionWidget := m.createSelectionWidget()
	rightLayout.AddWidget(selectionWidget, 0, 0)

	// Add machine widget
	m.machineWidget = NewMachineWidget(m.config, nil)
	rightLayout.AddWidget(m.machineWidget, 0, 0)
	m.registerCleanup(m.machineWidget)

	rightLayout.AddStretch(1)
}

// createSelectionWidget membuat widget pemilihan ukuran air
func (m *MainWindow) createSelectionWidget() *widgets.QWidget {
	widget := widgets.NewQWidget(nil, 0)
	widget.SetStyleSheet(`
		background-color: #F8F9FA;
		border-radius: 20px;
		border: 2px solid #E9ECEF;
		padding: 20px;
	`)

	layout := widgets.NewQVBoxLayout()
	widget.SetLayout(layout)

	// Title
	title := widgets.NewQLabel2("Select Water Size", nil, 0)
	title.SetStyleSheet(`
		font-size: 24px;
		font-weight: bold;
		color: #2C3E50;
		font-family: 'Segoe UI', Arial;
	`)
	title.SetAlignment(core.Qt__AlignCenter)

	// Grid untuk tombol
	buttonsGrid := widgets.NewQGridLayout(nil)
	buttonsGrid.SetSpacing(10)

	// Posisi tombol
	buttonPositions := []struct {
		size, imagePath string
		row, col       int
	}{
		{"100 ml", "1.png", 0, 0},
		{"350 ml", "2.png", 0, 1},
		{"600 ml", "3.png", 1, 0},
		{"1 Liter", "4.png", 1, 1},
	}

	m.sizeButtons = make([]*WaterButton, 0, len(buttonPositions))
	for _, pos := range buttonPositions {
		if volume, ok := models.WaterVolumes[pos.size]; ok {
			btn := NewWaterButton(volume.Name, volume.Price, pos.imagePath, nil)
			btn.ConnectClicked(m.createSizeButtonHandler(pos.size))
			buttonsGrid.AddWidget2(btn, pos.row, pos.col, 0)
			m.sizeButtons = append(m.sizeButtons, btn)
		}
	}

	layout.AddWidget(title, 0, 0)
	layout.AddLayout(buttonsGrid, 0)
	layout.AddStretch(1)

	return widget
}

// createSizeButtonHandler membuat handler untuk tombol ukuran
func (m *MainWindow) createSizeButtonHandler(size string) func(bool) {
	return func(checked bool) {
		// Uncheck tombol lain
		for _, btn := range m.sizeButtons {
			if btn.Text() != size {
				btn.SetChecked(false)
			}
		}

		// Set ukuran yang dipilih
		if checked {
			m.machineWidget.SetSelectedSize(size)
		} else {
			m.machineWidget.SetSelectedSize("")
		}
	}
}

// setupVideo menginisialisasi video thread
func (m *MainWindow) setupVideo() {
	m.videoThread = NewVideoThread(m.config.App.VideoPath)
	m.videoThread.ConnectFrameReady(func(image *gui.QImage) {
		if m.videoLabel == nil || image.IsNull() {
			return
		}

		size := m.videoLabel.Size()
		if !size.IsValid() {
			return
		}

		scaledPixmap := gui.NewQPixmap().FromImage(image, 0)
		scaledPixmap = scaledPixmap.Scaled2(
			size,
			core.Qt__KeepAspectRatio,
			core.Qt__SmoothTransformation,
		)

		if !scaledPixmap.IsNull() {
			m.videoLabel.SetPixmap(scaledPixmap)
		}
	})

	m.registerCleanup(m.videoThread)
	m.videoThread.Start()
}

// RegisterCleanup mendaftarkan handler untuk pembersihan
func (m *MainWindow) registerCleanup(handler interface{ Cleanup() }) {
	m.cleanupHandlers = append(m.cleanupHandlers, handler)
	m.logger.Debug("Registered cleanup handler: %T", handler)
}

// CloseEvent menangani event penutupan window
func (m *MainWindow) closeEvent(event *gui.QCloseEvent) {
	m.logger.Info("Application shutdown initiated")

	// Jalankan semua cleanup handlers
	for _, handler := range m.cleanupHandlers {
		m.logger.Debug("Running cleanup for: %T", handler)
		handler.Cleanup()
	}

	m.logger.Info("Application cleanup completed successfully")
	event.Accept()
}