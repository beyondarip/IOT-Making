package main

import (
    "os"
    
    "github.com/therecipe/qt/widgets"
    "github.com/therecipe/qt/core"
)

// MainWindow adalah window utama aplikasi
type MainWindow struct {
    widgets.QMainWindow

    // Widget utama
    centralWidget *widgets.QWidget
    mainLayout   *widgets.QVBoxLayout

    // Child widgets
    titleLabel *widgets.QLabel
    startButton *widgets.QPushButton
}

// NewMainWindow membuat instance baru MainWindow
func NewMainWindow(parent widgets.QWidget_ITF) *MainWindow {
    window := &MainWindow{
        QMainWindow: *widgets.NewQMainWindow(parent, 0),
    }
    
    window.init()
    return window
}

// init menginisialisasi UI
func (m *MainWindow) init() {
    // Set judul window
    m.SetWindowTitle("Water Vending Machine")
    
    // Buat widget utama
    m.centralWidget = widgets.NewQWidget(nil, 0)
    m.SetCentralWidget(m.centralWidget)
    
    // Buat layout utama
    m.mainLayout = widgets.NewQVBoxLayout()
    m.centralWidget.SetLayout(m.mainLayout)
    
    // Tambah label judul
    m.titleLabel = widgets.NewQLabel2("Water Vending Machine", nil, 0)
    m.titleLabel.SetAlignment(core.Qt__AlignCenter)
    m.mainLayout.AddWidget(m.titleLabel, 0, 0)
    
    // Tambah tombol start
    m.startButton = widgets.NewQPushButton2("Start", nil)
    m.startButton.ConnectClicked(func(checked bool) {
        widgets.QMessageBox_Information(nil, "Info", "Welcome to Water Vending Machine!", widgets.QMessageBox__Ok, widgets.QMessageBox__Ok)
    })
    m.mainLayout.AddWidget(m.startButton, 0, 0)

    // Set ukuran window
    m.Resize2(400, 300)
}

func main() {
    // Buat aplikasi Qt
    app := widgets.NewQApplication(len(os.Args), os.Args)
    
    // Buat dan tampilkan main window
    window := NewMainWindow(nil)
    window.Show()
    
    // Jalankan event loop
    app.Exec()
}