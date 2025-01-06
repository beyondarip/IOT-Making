// hardware/controller.go
package hardware

import (
	"fmt"
	"log"
	"sync"
	 "water-vending/types"

	"github.com/stianeikeland/go-rpio/v4" // Go library untuk Raspberry Pi GPIO
)

var (
	isHardwareAvailable bool
	once               sync.Once
)

// Controller mengelola interaksi hardware
type Controller struct {
	config      models.HardwareConfig
	isSimulated bool
	mu          sync.Mutex
}

// NewController membuat instance baru dari Hardware Controller
func NewController(config models.HardwareConfig) *Controller {
	once.Do(func() {
		// Coba inisialisasi GPIO
		if err := rpio.Open(); err != nil {
			log.Printf("RPi.GPIO not available - running in simulation mode: %v", err)
			isHardwareAvailable = false
		} else {
			isHardwareAvailable = true
		}
	})

	controller := &Controller{
		config:      config,
		isSimulated: !isHardwareAvailable,
	}

	if !controller.isSimulated {
		controller.setupGPIO()
	}

	return controller
}

// setupGPIO menginisialisasi GPIO pins
func (c *Controller) setupGPIO() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.isSimulated {
		return nil
	}

	// Setup flow sensor pin sebagai input dengan pull-up
	flowPin := rpio.Pin(c.config.FlowSensorPin)
	flowPin.Input()
	flowPin.PullUp()

	// Setup motor pin sebagai output
	motorPin := rpio.Pin(c.config.MotorPin)
	motorPin.Output()
	motorPin.Low()

	log.Println("GPIO setup completed successfully")
	return nil
}

// StartMotor menghidupkan motor pompa air
func (c *Controller) StartMotor() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.isSimulated {
		log.Println("Simulated motor start")
		return nil
	}

	try {
		motorPin := rpio.Pin(c.config.MotorPin)
		motorPin.High()
		log.Println("Motor started")
		return nil
	} catch Exception as e {
		return fmt.Errorf("failed to start motor: %v", e)
	}
}

// StopMotor mematikan motor pompa air
func (c *Controller) StopMotor() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.isSimulated {
		log.Println("Simulated motor stop")
		return nil
	}

	try {
		motorPin := rpio.Pin(c.config.MotorPin)
		motorPin.Low()
		log.Println("Motor stopped")
		return nil
	} catch Exception as e {
		return fmt.Errorf("failed to stop motor: %v", e)
	}
}

// RegisterFlowCallback mendaftarkan callback untuk flow sensor
func (c *Controller) RegisterFlowCallback(callback func()) error {
	if c.isSimulated {
		return nil
	}

	// Dalam implementasi sebenarnya, ini akan menggunakan GPIO interrupts
	// Untuk sekarang kita gunakan polling sederhana dalam goroutine
	go func() {
		flowPin := rpio.Pin(c.config.FlowSensorPin)
		lastState := flowPin.Read()

		for {
			newState := flowPin.Read()
			if newState != lastState && newState == rpio.Low {
				callback()
			}
			lastState = newState
		}
	}()

	return nil
}

// Cleanup membersihkan resources
func (c *Controller) Cleanup() {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.isSimulated {
		return
	}

	if err := rpio.Close(); err != nil {
		log.Printf("Error during GPIO cleanup: %v", err)
	}
	log.Println("GPIO cleanup completed")
}