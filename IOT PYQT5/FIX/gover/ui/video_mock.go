// ui/video_mock.go
package ui

import (
    "time"

    "github.com/therecipe/qt/core"
    "github.com/therecipe/qt/gui"
)

// MockVideoThread menyediakan simulasi video untuk development
type MockVideoThread struct {
    core.QObject

    // Signals
    _ func(image *gui.QImage) `signal:"frameReady"`

    running bool
}

func NewMockVideoThread() *MockVideoThread {
    thread := &MockVideoThread{
        QObject: *core.NewQObject(nil),
    }
    return thread
}

func (v *MockVideoThread) Start() {
    v.running = true
    go v.simulateVideo()
}

func (v *MockVideoThread) simulateVideo() {
    // Buat gambar test pattern
    image := gui.NewQImage2(nil, 640, 480, gui.QImage__Format_RGB888)
    image.Fill3(gui.NewQColor3(200, 200, 200))

    for v.running {
        v.FrameReady(image)
        time.Sleep(33 * time.Millisecond) // ~30 FPS
    }
}

func (v *MockVideoThread) Stop() {
    v.running = false
}

func (v *MockVideoThread) Cleanup() {
    v.Stop()
}