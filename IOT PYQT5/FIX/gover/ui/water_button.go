// ui/water_button.go
package ui

import (
	"os"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
	"github.com/therecipe/qt/widgets"
)

// WaterButton adalah custom button untuk pemilihan volume air
type WaterButton struct {
	widgets.QPushButton

	iconContainer *widgets.QLabel
	sizeLabel     *widgets.QLabel
	layout        *widgets.QVBoxLayout
}

// NewWaterButton membuat instance baru WaterButton
func NewWaterButton(sizeText, priceText, imagePath string, parent widgets.QWidget_ITF) *WaterButton {
	button := &WaterButton{
		QPushButton: *widgets.NewQPushButton(parent),
	}
	button.init(sizeText, priceText, imagePath)
	return button
}

// init menginisialisasi komponen UI button
func (b *WaterButton) init(sizeText, priceText, imagePath string) {
	// Set size policy dan ukuran tetap
	b.SetSizePolicy2(
		widgets.QSizePolicy__Fixed,
		widgets.QSizePolicy__Fixed,
	)
	b.SetFixedSize2(150, 150)
	b.SetCheckable(true)

	// Buat layout
	b.layout = widgets.NewQVBoxLayout()
	b.layout.SetSpacing(5)
	b.layout.SetContentsMargins(10, 10, 10, 10)

	// Container icon
	b.iconContainer = widgets.NewQLabel(nil, 0)
	b.iconContainer.SetFixedSize2(80, 80)
	b.iconContainer.SetStyleSheet(`
		background-color: white;
		border-radius: 10px;
		padding: 5px;
	`)

	// Load dan set image jika ada
	if _, err := os.Stat(imagePath); err == nil {
		pixmap := gui.NewQPixmap3(imagePath)
		scaledPixmap := pixmap.Scaled2(
			70, 70,
			core.Qt__KeepAspectRatio,
			core.Qt__SmoothTransformation,
		)
		b.iconContainer.SetPixmap(scaledPixmap)
	}
	b.iconContainer.SetAlignment(core.Qt__AlignCenter)

	// Label untuk ukuran dan harga
	b.sizeLabel = widgets.NewQLabel2(sizeText+"\n"+priceText, nil, 0)
	b.sizeLabel.SetAlignment(core.Qt__AlignCenter)
	b.sizeLabel.SetStyleSheet(`
		color: #2C3E50;
		font-size: 16px;
		font-weight: bold;
		font-family: 'Segoe UI', Arial;
	`)

	// Tambahkan widgets ke layout
	b.layout.AddWidget(b.iconContainer, 0, core.Qt__AlignCenter)
	b.layout.AddWidget(b.sizeLabel, 0, core.Qt__AlignCenter)

	// Set layout ke button
	b.SetLayout(b.layout)

	// Set stylesheet untuk button
	b.SetStyleSheet(`
		WaterButton {
			background-color: #F8F9FA;
			border-radius: 15px;
			border: 2px solid #E9ECEF;
		}
		WaterButton:checked {
			background-color: #4EA8DE;
			border: 2px solid #5390D9;
		}
		WaterButton:checked QLabel {
			color: white;
		}
		WaterButton:hover {
			background-color: #E9ECEF;
			border: 2px solid #DEE2E6;
		}
	`)
}