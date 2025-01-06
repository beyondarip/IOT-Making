// hardware/gpio_mock.go
package hardware

import (
    "fmt"
    "sync"
)

// MockGPIO menyediakan simulasi GPIO untuk development
type MockGPIO struct {
    pins map[int]bool
    mu   sync.RWMutex
}

var (
    mockInstance *MockGPIO
    mockOnce     sync.Once
)

// GetMockGPIO returns singleton instance of MockGPIO
func GetMockGPIO() *MockGPIO {
    mockOnce.Do(func() {
        mockInstance = &MockGPIO{
            pins: make(map[int]bool),
        }
    })
    return mockInstance
}

func (m *MockGPIO) SetPin(pin int, state bool) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.pins[pin] = state
}

func (m *MockGPIO) GetPin(pin int) bool {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return m.pins[pin]
}

// Mock interface matching original GPIO
type Pin int

const (
    Input = iota
    Output
    Clock
    Pwm
    High = true
    Low  = false
)

func Open() error {
    return nil
}

func Close() error {
    return nil
}

func (p Pin) Input() {
    GetMockGPIO().SetPin(int(p), false)
}

func (p Pin) Output() {
    GetMockGPIO().SetPin(int(p), false)
}

func (p Pin) High() {
    GetMockGPIO().SetPin(int(p), true)
}

func (p Pin) Low() {
    GetMockGPIO().SetPin(int(p), false)
}

func (p Pin) Read() bool {
    return GetMockGPIO().GetPin(int(p))
}