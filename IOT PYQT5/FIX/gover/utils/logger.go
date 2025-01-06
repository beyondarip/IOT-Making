// utils/logger.go
package utils

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

var (
	logger *Logger
	once   sync.Once
)

// LogLevel mendefinisikan level logging
type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARNING
	ERROR
	CRITICAL
)

// Logger adalah custom logger dengan multiple outputs
type Logger struct {
	*log.Logger
	file   *os.File
	level  LogLevel
	mu     sync.Mutex
}

// InitLogger menginisialisasi logger dengan file dan console output
func InitLogger(filename string, level LogLevel) (*Logger, error) {
	var err error
	once.Do(func() {
		logger, err = newLogger(filename, level)
	})
	return logger, err
}

// GetLogger mengembalikan instance logger yang sudah diinisialisasi
func GetLogger() *Logger {
	if logger == nil {
		panic("Logger not initialized. Call InitLogger first")
	}
	return logger
}

// newLogger membuat instance baru logger
func newLogger(filename string, level LogLevel) (*Logger, error) {
	// Buat direktori log jika belum ada
	if err := os.MkdirAll(filepath.Dir(filename), 0755); err != nil {
		return nil, fmt.Errorf("failed to create log directory: %v", err)
	}

	// Buka file log
	file, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		return nil, fmt.Errorf("failed to open log file: %v", err)
	}

	// Setup multi-writer untuk file dan console
	multiWriter := io.MultiWriter(file, os.Stdout)

	l := &Logger{
		Logger: log.New(multiWriter, "", 0),
		file:   file,
		level:  level,
	}

	return l, nil
}

// formatMessage memformat pesan log dengan timestamp dan info tambahan
func (l *Logger) formatMessage(level LogLevel, format string, args ...interface{}) string {
	// Get caller information
	_, file, line, ok := runtime.Caller(2)
	if !ok {
		file = "unknown"
		line = 0
	}
	
	// Ambil nama file saja tanpa path
	file = filepath.Base(file)

	// Format timestamp
	timestamp := time.Now().Format("2006-01-02 15:04:05")

	// Format level sebagai string
	levelStr := [...]string{"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}[level]

	// Format message
	var msg string
	if len(args) > 0 {
		msg = fmt.Sprintf(format, args...)
	} else {
		msg = format
	}

	return fmt.Sprintf("%s - %s - %s:%d - %s", 
		timestamp, levelStr, file, line, msg)
}

// Log methods
func (l *Logger) Debug(format string, args ...interface{}) {
	if l.level <= DEBUG {
		l.mu.Lock()
		l.Println(l.formatMessage(DEBUG, format, args...))
		l.mu.Unlock()
	}
}

func (l *Logger) Info(format string, args ...interface{}) {
	if l.level <= INFO {
		l.mu.Lock()
		l.Println(l.formatMessage(INFO, format, args...))
		l.mu.Unlock()
	}
}

func (l *Logger) Warning(format string, args ...interface{}) {
	if l.level <= WARNING {
		l.mu.Lock()
		l.Println(l.formatMessage(WARNING, format, args...))
		l.mu.Unlock()
	}
}

func (l *Logger) Error(format string, args ...interface{}) {
	if l.level <= ERROR {
		l.mu.Lock()
		l.Println(l.formatMessage(ERROR, format, args...))
		l.mu.Unlock()
	}
}

func (l *Logger) Critical(format string, args ...interface{}) {
	if l.level <= CRITICAL {
		l.mu.Lock()
		l.Println(l.formatMessage(CRITICAL, format, args...))
		l.mu.Unlock()
	}
}

// Close menutup file log
func (l *Logger) Close() error {
	l.mu.Lock()
	defer l.mu.Unlock()
	
	if l.file != nil {
		if err := l.file.Close(); err != nil {
			return fmt.Errorf("failed to close log file: %v", err)
		}
		l.file = nil
	}
	return nil
}