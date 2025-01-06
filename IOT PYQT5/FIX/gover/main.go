// main.go
package main

import (
    "os"
    "water-vending/config"
    "water-vending/ui"
    "water-vending/utils"

    "github.com/therecipe/qt/gui"
    "github.com/therecipe/qt/widgets"
)

func init() {
    // Set environment untuk development
    os.Setenv("DEVELOPMENT_MODE", "true")
}

func main() {
    // Initialize logger
    logger, err := utils.InitLogger("vending_machine.log", utils.INFO)
    if err != nil {
        panic("Failed to initialize logger: " + err.Error())
    }
    defer logger.Close()

    logger.Info("Starting application in development mode")

    // Load configuration
    config := config.GetInstance().GetConfig()

    // Create application
    app := widgets.NewQApplication(len(os.Args), os.Args)

    // Set application-wide font
    font := gui.NewQFont2("Segoe UI", 10, -1, false)
    app.SetFont(font)

    // Create and show main window
    window := ui.NewMainWindow(config)
    window.Show()

    // Start event loop
    os.Exit(app.Exec())
}