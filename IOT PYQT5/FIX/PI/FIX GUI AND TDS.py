import sys
import math
import time
import board
import busio
import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("vending_machine.log"),
        logging.StreamHandler()
    ]
)

# GPIO Configuration
FLOW_SENSOR_PIN = 20
MOTOR_PIN = 21
TARGET_PULSES = {
    '300 ML\n(Regular)': 325,  # Calibrated for 300ml
    '600 ML\n(Medium)': 670,   # Calibrated for 600ml
    '1.5 L\n(Large)': 2400     # Calibrated for 1.5L
}

# TDS Configuration
VREF = 5.0
TDS_FACTOR = 0.5
TEMPERATURE = 25.0

class TDSSensor(QObject):
    tds_updated = pyqtSignal(float, float)  # Signal for voltage and TDS value

    def __init__(self):
        super().__init__()
        # Initialize I2C and ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.gain = 1
        self.chan = AnalogIn(self.ads, ADS.P0)
        self.running = True

    def calculate_tds(self, voltage, temperature=25.0):
        temp_coefficient = 1.0 + 0.02 * (temperature - 25.0)
        tds_value = ((133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5) / temp_coefficient
        return tds_value

    def run(self):
        while self.running:
            try:
                voltage = self.chan.voltage
                tds_value = self.calculate_tds(voltage, TEMPERATURE)
                self.tds_updated.emit(voltage, tds_value)
                time.sleep(1)
            except Exception as e:
                logging.error(f"TDS Sensor error: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False

class TDSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Create labels with styling
        self.tds_label = QLabel('TDS Monitor')
        self.tds_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: rgba(52, 152, 219, 0.3);
            padding: 10px;
            border-radius: 10px;
        """)
        self.tds_label.setAlignment(Qt.AlignCenter)
        
        self.value_label = QLabel('--- ppm')
        self.value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2ecc71;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.tds_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def update_values(self, voltage, tds):
        self.value_label.setText(f"{tds:.0f} ppm")

class WaterController(QObject):
    update_progress = pyqtSignal(int)
    filling_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pulse_count = 0
        self.is_running = False
        self.target_pulses = 0
        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(MOTOR_PIN, GPIO.OUT)
        GPIO.output(MOTOR_PIN, GPIO.LOW)

    def pulse_callback(self, channel):
        if not self.is_running:
            return

        self.pulse_count += 1
        logging.info(f"Pulse detected: {self.pulse_count}/{self.target_pulses}")
        progress = int((self.pulse_count / self.target_pulses) * 100)
        progress = min(100, progress)  # Ensure we don't exceed 100%
        self.update_progress.emit(progress)

        if self.pulse_count >= self.target_pulses:
            self.stop_filling()

    def start_filling(self, size):
        if size not in TARGET_PULSES:
            logging.error("Invalid size selected.")
            return False

        self.target_pulses = TARGET_PULSES[size]
        self.pulse_count = 0
        self.is_running = True
        logging.info(f"Starting filling process for {size} with target {self.target_pulses} pulses.")

        # Start motor in a separate thread
        threading.Thread(target=self._filling_process, daemon=True).start()
        return True

    def _filling_process(self):
        try:
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, 
                                  callback=self.pulse_callback)

            while self.is_running:
                QThread.msleep(100)

        except Exception as e:
            logging.error(f"Error in filling process: {e}")
            self.stop_filling()

    def stop_filling(self):
        self.is_running = False
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        try:
            GPIO.remove_event_detect(FLOW_SENSOR_PIN)
        except Exception as e:
            logging.warning(f"Failed to remove event detection: {e}")
        self.filling_complete.emit()
        logging.info(f"Filling process completed. Total pulses: {self.pulse_count}. Target pulses: {self.target_pulses}.")

    def cleanup(self):
        self.stop_filling()
        GPIO.cleanup()
        logging.info("GPIO cleanup done.")

class CircularButton(QPushButton):
    def __init__(self, text, size=180):
        super().__init__()
        self.setText(text)
        self.setFixedSize(size, size)
        self.setCheckable(True)
        self.ripple_pos = QPoint()
        self.ripple_radius = 0
        self.ripple_opacity = 0
        self.ripple_animation = QVariantAnimation()
        self.ripple_animation.setStartValue(0)
        self.ripple_animation.setEndValue(size)
        self.ripple_animation.setDuration(500)
        self.ripple_animation.valueChanged.connect(self.update_ripple)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def update_ripple(self, value):
        self.ripple_radius = value
        self.ripple_opacity = max(0, 1 - value/self.width())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw button background
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())

        gradient = QRadialGradient(self.rect().center(), self.width())
        if self.isChecked():
            gradient.setColorAt(0, QColor(41, 128, 185))
            gradient.setColorAt(1, QColor(52, 152, 219))
        else:
            gradient.setColorAt(0, QColor(52, 152, 219, 200))
            gradient.setColorAt(1, QColor(41, 128, 185, 200))

        painter.fillPath(path, gradient)

        # Glass effect
        glass = QPainterPath()
        glass.addEllipse(5, 5, self.width()-10, self.height()/2-5)
        glass_gradient = QLinearGradient(0, 0, 0, self.height()/2)
        glass_gradient.setColorAt(0, QColor(255, 255, 255, 100))
        glass_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(glass, glass_gradient)

        # Draw text
        font = QFont('Arial', 14, QFont.Bold)
        if "\n" in self.text():
            font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

        # Draw ripple effect
        if self.ripple_radius > 0:
            painter.setOpacity(self.ripple_opacity)
            painter.setBrush(QColor(255, 255, 255, 50))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.ripple_pos, self.ripple_radius, self.ripple_radius)

    def mousePressEvent(self, event):
        self.ripple_pos = event.pos()
        self.ripple_animation.start()
        super().mousePressEvent(event)

class WaveContainer(QFrame):
    def __init__(self):
        super().__init__()
        self.water_level = 0
        self.wave_offset = 0
        self.setMinimumSize(300, 500)
        
        # Wave animation
        self.wave_timer = QTimer()
        self.wave_timer.timeout.connect(self.update_wave)
        self.wave_timer.start(50)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def update_wave(self):
        self.wave_offset += 5
        if self.wave_offset > 360:
            self.wave_offset = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Container dimensions
        width = self.width() - 20
        height = self.height() - 20
        x = 10
        y = 10

        # Draw container
        container = QPainterPath()
        container.addRoundedRect(x, y, width, height, 30, 30)
        
        # Glass effect gradient
        glass_gradient = QLinearGradient(x, y, width + x, height + y)
        glass_gradient.setColorAt(0, QColor(255, 255, 255, 30))
        glass_gradient.setColorAt(0.5, QColor(255, 255, 255, 15))
        glass_gradient.setColorAt(1, QColor(255, 255, 255, 30))
        
        painter.fillPath(container, glass_gradient)
        painter.strokePath(container, QPen(QColor(255, 255, 255, 50), 2))

        # Calculate water height
        water_height = int(height * (self.water_level / 100))
        if water_height > 0:
            # Create wave path
            wave = QPainterPath()
            wave.moveTo(x, y + height - water_height)
            
            # Generate wave points
            for i in range(width + 1):
                wave_y = 10 * math.sin((i + self.wave_offset) * 0.05)
                wave.lineTo(x + i, y + height - water_height + wave_y)
            
            wave.lineTo(x + width, y + height)
            wave.lineTo(x, y + height)
            wave.closeSubpath()

            # Water gradient with waves
            water_gradient = QLinearGradient(0, y + height - water_height, 0, y + height)
            water_gradient.setColorAt(0, QColor(52, 152, 219, 200))
            water_gradient.setColorAt(1, QColor(41, 128, 185, 200))
            
            painter.fillPath(wave, water_gradient)

        # Draw percentage
        font = QFont('Arial', 20, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        percentage_text = f"{self.water_level}%"
        painter.drawText(self.rect(), Qt.AlignCenter, percentage_text)

class ModernButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFixedSize(250, 70)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Button gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        if self.isEnabled():
            gradient.setColorAt(0, QColor(46, 204, 113))
            gradient.setColorAt(1, QColor(39, 174, 96))
        else:
            gradient.setColorAt(0, QColor(189, 195, 199))
            gradient.setColorAt(1, QColor(127, 140, 141))

        # Draw rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 35, 35)
        painter.fillPath(path, gradient)

        # Glass effect
        glass = QLinearGradient(0, 0, 0, self.height()/2)
        glass.setColorAt(0, QColor(255, 255, 255, 70))
        glass.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(path, glass)

        # Text
        font = QFont('Arial', 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.water_controller = WaterController()
        self.water_controller.update_progress.connect(self.update_water_level)
        self.water_controller.filling_complete.connect(self.filling_completed)
        
        # Initialize TDS Sensor
        self.tds_sensor = TDSSensor()
        self.tds_thread = QThread()
        self.tds_sensor.moveToThread(self.tds_thread)
        self.tds_thread.started.connect(self.tds_sensor.run)
        self.tds_thread.start()
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Premium Water Vending')
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000428, stop:1 #004e92);
            }
            QGroupBox {
                background: rgba(255, 255, 255, 10);
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 25px;
                margin-top: 35px;
            }
            QLabel {
                color: white;
                font-family: 'Arial';
            }
        """)
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)

        # Create top bar for title and TDS
        top_bar = QHBoxLayout()
        
        # Title (now in top bar)
        title = QLabel('PREMIUM WATER VENDING')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        """)
        
        # Add TDS Widget
        self.tds_widget = TDSWidget()
        self.tds_sensor.tds_updated.connect(self.tds_widget.update_values)
        
        top_bar.addWidget(title, stretch=7)
        top_bar.addWidget(self.tds_widget, stretch=3)
        layout.addLayout(top_bar)
        
        # Size selection
        size_group = QGroupBox("SELECT YOUR SIZE")
        size_layout = QHBoxLayout()
        size_layout.setSpacing(30)
        
        self.size_buttons = []
        sizes = [('300 ML\n(Regular)', 'Rp. 3.000'), 
                ('600 ML\n(Medium)', 'Rp. 7.000'), 
                ('1.5 L\n(Large)', 'Rp. 15.000')]
        
        for size, price in sizes:
            btn = CircularButton(f"{size}\n{price}")
            btn.clicked.connect(lambda checked, s=size: self.select_size(s))
            size_layout.addWidget(btn)
            self.size_buttons.append(btn)
            
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Fill button
        self.fill_button = ModernButton('START FILLING')
        self.fill_button.setEnabled(False)
        self.fill_button.clicked.connect(self.start_filling)
        layout.addWidget(self.fill_button, alignment=Qt.AlignCenter)
        
        # Water container
        container_wrapper = QWidget()
        container_layout = QHBoxLayout(container_wrapper)
        self.container = WaveContainer()
        container_layout.addWidget(self.container)
        layout.addWidget(container_wrapper)
        
        # Animation setup
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_water_level)
        
        self.selected_size = None
        self.is_filling = False
        
        self.setMinimumSize(900, 1000)
        self.center()

    def center(self):
        frame = self.frameGeometry()
        screen = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(screen)
        self.move(frame.topLeft())
        
    def select_size(self, size):
        self.selected_size = size
        self.fill_button.setEnabled(True)
        
        for btn in self.size_buttons:
            btn.setChecked(btn.text().startswith(size))

    def start_filling(self):
        if not self.is_filling and self.selected_size:
            self.is_filling = True
            self.container.water_level = 0
            self.fill_button.setEnabled(False)
            for btn in self.size_buttons:
                btn.setEnabled(False)
            
            # Start the water controller
            success = self.water_controller.start_filling(self.selected_size)
            if not success:
                self.filling_completed()  # Reset UI if start failed

    def update_water_level(self, level):
        self.container.water_level = level
        self.container.update()

    def filling_completed(self):
        self.is_filling = False
        self.fill_button.setEnabled(True)
        for btn in self.size_buttons:
            btn.setEnabled(True)

    def closeEvent(self, event):
        self.tds_sensor.stop()
        self.tds_thread.quit()
        self.tds_thread.wait()
        self.water_controller.cleanup()
        event.accept()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        vending_machine = VendingMachine()
        vending_machine.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        GPIO.output(MOTOR_PIN, GPIO.LOW)
        GPIO.cleanup()
        logging.info("Program interrupted by user. Motor stopped and GPIO cleaned up.")
    except Exception as e:
        logging.error(f"Application error: {e}")
        GPIO.cleanup()
