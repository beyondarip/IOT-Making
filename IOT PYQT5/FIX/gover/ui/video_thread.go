// ui/video_thread.go
package ui

import (
	"sync"
	"time"
	"water-vending/utils"

	"github.com/therecipe/qt/core"
	"github.com/therecipe/qt/gui"
	"gocv.io/x/gocv"
)

// VideoThread menangani pemutaran video dalam goroutine terpisah
type VideoThread struct {
	core.QObject

	// Signals
	_ func(image *gui.QImage) `signal:"frameReady"`

	videoPath string
	running   bool
	mutex     sync.Mutex
	logger    *utils.Logger
}

// NewVideoThread membuat instance baru VideoThread
func NewVideoThread(videoPath string) *VideoThread {
	thread := &VideoThread{
		QObject:   *core.NewQObject(nil),
		videoPath: videoPath,
		logger:    utils.GetLogger(),
	}
	return thread
}

// Start memulai thread video
func (v *VideoThread) Start() {
	v.mutex.Lock()
	v.running = true
	v.mutex.Unlock()

	go v.run()
}

// run adalah main loop untuk video processing
func (v *VideoThread) run() {
	// Buka video capture
	cap, err := gocv.OpenVideoCapture(v.videoPath)
	if err != nil {
		v.logger.Error("Failed to open video file: %v", err)
		return
	}
	defer cap.Close()

	img := gocv.NewMat()
	defer img.Close()

	for v.isRunning() {
		if ok := cap.Read(&img); !ok {
			// Reset video ke awal jika sudah selesai
			cap.Set(gocv.VideoCapturePosProp, 0)
			continue
		}

		// Convert BGR ke RGB
		gocv.CvtColor(img, &img, gocv.ColorBGRToRGB)

		// Convert ke QImage
		height := img.Rows()
		width := img.Cols()
		bytesPerLine := img.Cols() * 3 // 3 channels (RGB)

		// Create QImage dari data gambar
		qimg := gui.NewQImage2(
			img.DataPtrUint8(),
			width,
			height,
			bytesPerLine,
			gui.QImage__Format_RGB888,
			nil,
			nil,
		)

		// Copy image karena data original akan di-free setelah loop
		qimgCopy := qimg.Copy()

		// Emit signal dengan image baru
		v.FrameReady(qimgCopy)

		// Sleep untuk mencapai ~30 FPS
		time.Sleep(33 * time.Millisecond)
	}
}

// Stop menghentikan thread video
func (v *VideoThread) Stop() {
	v.mutex.Lock()
	v.running = false
	v.mutex.Unlock()
}

// isRunning memeriksa status thread
func (v *VideoThread) isRunning() bool {
	v.mutex.Lock()
	defer v.mutex.Unlock()
	return v.running
}

// Cleanup membersihkan resources
func (v *VideoThread) Cleanup() {
	v.Stop()
}