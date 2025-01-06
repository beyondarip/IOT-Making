import sys
import json
import math
import random
import time
import logging
import threading
import wave
import pyaudio
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QProgressBar, QMessageBox, QSplashScreen,
    QStatusBar, QSystemTrayIcon, QMenu, 
)
from PyQt5.QtMultimediaWidgets import QVideoWidget  # Pindahkan import ini ke sini
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import (
    Qt, QTimer, QSize, QUrl, QPropertyAnimation, QEasingCurve, 
    QThread, pyqtSignal, QSettings
)
from PyQt5.QtGui import (
    QFont, QIcon, QImage, QPixmap, QPainter, QPen, QColor, 
    QLinearGradient, QPainterPath, 
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, QUrl, QPropertyAnimation, QEasingCurve, 
    QThread, pyqtSignal, QSettings, QRectF  # QRectF moved here
)
from PyQt5.QtWidgets import QStyle
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class WaterAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 300)
        self.progress = 0
        self.is_filling = False
        
        # Create wave effect
        self.wave_points = []
        self.wave_offset = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(50)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw container
        container = self.rect().adjusted(10, 10, -10, -10)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(container)
        
        # Calculate water height based on progress
        water_height = container.height() * (self.progress / 100)
        water_rect = QRectF(
            container.x(),
            container.y() + container.height() - water_height,
            container.width(),
            water_height
        )
        
        # Create water gradient
        gradient = QLinearGradient(
            water_rect.topLeft(),
            water_rect.bottomLeft()
        )
        gradient.setColorAt(0, QColor(78, 171, 255, 200))
        gradient.setColorAt(1, QColor(28, 127, 238, 200))
        
        # Draw water with wave effect
        path = QPainterPath()
        path.moveTo(water_rect.x(), water_rect.y() + water_rect.height())
        
        # Generate wave points
        wave_width = water_rect.width()
        for x in range(int(water_rect.x()), int(water_rect.x() + wave_width), 10):
            y = water_rect.y() + math.sin(x/50 + self.wave_offset) * 5
            if x == water_rect.x():
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
                
        path.lineTo(water_rect.x() + wave_width, water_rect.y() + water_rect.height())
        path.lineTo(water_rect.x(), water_rect.y() + water_rect.height())
        
        painter.fillPath(path, gradient)
        
    def update_wave(self):
        self.wave_offset += 0.2
        if self.is_filling:
            self.progress = min(100, self.progress + 0.5)
        self.update()
        
    def start_filling(self):
        self.is_filling = True
        self.progress = 0
        
    def stop_filling(self):
        self.is_filling = False

class WaterQualitySensor(QThread):
    quality_updated = pyqtSignal(float, int)  # pH, TDS
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # Simulate reading from sensors
                ph = 7.0 + random.uniform(-0.2, 0.2)
                tds = 50 + random.randint(-5, 5)
                self.quality_updated.emit(ph, tds)
            except Exception as e:
                logging.error(f"Sensor reading error: {str(e)}")
            self.msleep(1000)  # Update every second
            
    def stop(self):
        self.running = False

class TransactionLogger:
    def __init__(self):
        self.log_file = "transactions.json"
        self.ensure_log_file()
        
    def ensure_log_file(self):
        try:
            with open(self.log_file, 'a+') as f:
                f.seek(0)
                if not f.read():
                    json.dump([], f)
        except Exception as e:
            logging.error(f"Error initializing log file: {str(e)}")
    
    def log_transaction(self, size, amount_paid, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        transaction = {
            "size": size,
            "amount_paid": amount_paid,
            "timestamp": timestamp
        }
        
        try:
            with open(self.log_file, 'r+') as f:
                try:
                    transactions = json.load(f)
                except json.JSONDecodeError:
                    transactions = []
                
                transactions.append(transaction)
                f.seek(0)
                f.truncate()
                json.dump(transactions, f, indent=4)
        except Exception as e:
            logging.error(f"Error logging transaction: {str(e)}")

class WaterVendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_logging()
        self.load_settings()
        self.init_splash_screen()
        self.setup_system_tray()
        self.initUI()
        self.setup_video_player()
        self.setup_audio()
        self.setup_sensors()
        self.setup_status_bar()
        self.transaction_logger = TransactionLogger()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='vending_machine.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def init_splash_screen(self):
        splash_pixmap = QPixmap("splash.png")
        splash = QSplashScreen(splash_pixmap)
        splash.show()
        QApplication.processEvents()
        time.sleep(2)
        splash.finish(self)
        
    def load_settings(self):
        self.settings = QSettings('VendingCo', 'WaterVending')
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.showNormal)
        hide_action = tray_menu.addAction("Minimize")
        hide_action.triggered.connect(self.hide)
        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def initUI(self):
        self.setWindowTitle('Smart Water Vending Machine')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F8FF;
            }
            QPushButton {
                background-color: #4FB0FF;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d8cd6;
            }
            QPushButton:pressed {
                background-color: #2d6dad;
            }
            QLabel {
                color: #2C3E50;
                font-size: 16px;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header = QLabel("Select Water Size")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont('Arial', 24, QFont.Bold))
        self.main_layout.addWidget(header)
        
        # Water animation widget
        self.water_animation = WaterAnimation()
        self.main_layout.addWidget(self.water_animation)
        
        # Bottle size selection grid
        size_grid = QGridLayout()
        self.bottle_buttons = []
        sizes = [
            ("100ml", "100ml.png", 0, 0),
            ("350ml", "350ml.png", 0, 1),
            ("600ml", "600ml.png", 1, 0),
            ("1 Liter", "1l.png", 1, 1)
        ]
        
        for size, icon_path, row, col in sizes:
            bottle_frame = QFrame()
            bottle_layout = QVBoxLayout(bottle_frame)
            
            try:
                icon = QIcon(f":/images/{icon_path}")
                button = QPushButton()
                button.setIcon(icon)
                button.setIconSize(QSize(100, 100))
            except:
                button = QPushButton("🍶")
                button.setFont(QFont('Arial', 32))
            
            button.setFixedSize(200, 200)
            button.setCheckable(True)
            button.clicked.connect(self.bottle_selected)
            self.bottle_buttons.append(button)
            
            label = QLabel(size)
            label.setAlignment(Qt.AlignCenter)
            
            bottle_layout.addWidget(button)
            bottle_layout.addWidget(label)
            size_grid.addWidget(bottle_frame, row, col)
        
        self.main_layout.addLayout(size_grid)
        
        # Water quality indicators
        quality_frame = QFrame()
        quality_layout = QHBoxLayout(quality_frame)
        
        # pH Value
        ph_layout = QVBoxLayout()
        ph_label = QLabel("pH Value")
        self.ph_value = QLabel("7.0")
        self.ph_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #27AE60;")
        ph_layout.addWidget(ph_label, alignment=Qt.AlignCenter)
        ph_layout.addWidget(self.ph_value, alignment=Qt.AlignCenter)
        
        # TDS Value
        tds_layout = QVBoxLayout()
        tds_label = QLabel("TDS Value")
        self.tds_value = QLabel("50 ppm")
        self.tds_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #27AE60;")
        tds_layout.addWidget(tds_label, alignment=Qt.AlignCenter)
        tds_layout.addWidget(self.tds_value, alignment=Qt.AlignCenter)
        
        quality_layout.addLayout(ph_layout)
        quality_layout.addLayout(tds_layout)
        self.main_layout.addWidget(quality_frame)
        
        # Start button
        self.start_button = QPushButton("Start Filling")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_filling)
        self.start_button.setFixedHeight(60)
        self.main_layout.addWidget(self.start_button)
        
        # Initialize window size
        self.resize(800, 900)
        self.setMinimumSize(600, 700)
        
    def setup_video_player(self):
        # Create video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(320, 180)
        
        # Create media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Load video file
        video_path = "ad_video.mp4"
        self.media_player.setMedia(
            QMediaContent(QUrl.fromLocalFile(video_path))
        )
        
        # Add video widget to layout
        self.main_layout.insertWidget(1, self.video_widget)
        
        # Set video to loop
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.media_player.play()
        
    def setup_audio(self):
        self.audio_thread = None
        self.is_playing_sound = False
        
    def setup_sensors(self):
        self.sensor_thread = WaterQualitySensor()
        self.sensor_thread.quality_updated.connect(self.update_water_quality)
        self.sensor_thread.start()
        
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def bottle_selected(self):
        sender = self.sender()
        for button in self.bottle_buttons:
            if button != sender:
                button.setChecked(False)
        self.start_button.setEnabled(sender.isChecked())
        
    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
            
    def play_filling_sound(self):
        def audio_worker():
            CHUNK = 1024
            wf = wave.open('filling_sound.wav', 'rb')
            p = pyaudio.PyAudio()
            
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                          channels=wf.getnchannels(),
                          rate=wf.getframerate(),
                          output=True)
            
            data = wf.readframes(CHUNK)
            while data and self.is_playing_sound:
                stream.write(data)
                data = wf.readframes(CHUNK)
                
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        self.is_playing_sound = True
        self.audio_thread = threading.Thread(target=audio_worker)
        self.audio_thread.start()
        
    def stop_filling_sound(self):
        self.is_playing_sound = False
        if self.audio_thread:
            self.audio_thread.join()
            
    def show_error(self, message, title="Error"):
        QMessageBox.critical(self, title, message)
        logging.error(f"{title}: {message}")
        
    def show_warning(self, message, title="Warning"):
        QMessageBox.warning(self, title, message)
        logging.warning(f"{title}: {message}")
        
    def show_info(self, message, title="Information"):
        QMessageBox.information(self, title, message)
        logging.info(f"{title}: {message}")

    def process_payment(self, amount):
        try:
            # Simulate payment processing
            # In real implementation, integrate with payment gateway
            time.sleep(1)
            return True
        except Exception as e:
            self.show_error(f"Payment processing error: {str(e)}")
            return False
            
    def start_filling(self):
        selected_size = None
        for button, size in zip(self.bottle_buttons, ["100ml", "350ml", "600ml", "1L"]):
            if button.isChecked():
                selected_size = size
                break
                
        if not selected_size:
            self.show_warning("Please select a bottle size")
            return
            
        # Check water quality before proceeding
        try:
            ph = float(self.ph_value.text())
            tds = int(self.tds_value.text().split()[0])
            
            if not (6.5 <= ph <= 8.5):
                self.show_error("pH levels are outside safe range")
                return
                
            if not (0 <= tds <= 100):
                self.show_error("TDS levels are outside safe range")
                return
        except ValueError as e:
            self.show_error(f"Error reading water quality values: {str(e)}")
            return
            
        # Process payment (simplified)
        if not self.process_payment(1.00):  # $1.00 for demonstration
            return
            
        # Disable bottle selection
        for button in self.bottle_buttons:
            button.setEnabled(False)
        self.start_button.setEnabled(False)
        
        # Start water animation
        self.water_animation.start_filling()
        self.play_filling_sound()
        
        # Create progress bar animation
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2C3E50;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                width: 10px;
                margin: 0.5px;
            }
        """)
        self.main_layout.addWidget(self.progress_bar)
        
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(10000)  # 10 seconds to fill
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(100)
        self.progress_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Connect animation finished signal
        self.progress_animation.finished.connect(self.filling_completed)
        self.progress_animation.start()
        
        # Log transaction
        try:
            self.status_bar.showMessage(f"Filling {selected_size} bottle...")
            self.transaction_logger.log_transaction(selected_size, 1.00)
        except Exception as e:
            self.show_error(f"Error during filling process: {str(e)}")
            return
            
    def filling_completed(self):
        # Stop animations and sound
        self.water_animation.stop_filling()
        self.stop_filling_sound()
        
        # Re-enable controls
        for button in self.bottle_buttons:
            button.setEnabled(True)
        self.start_button.setEnabled(True)
        
        # Remove progress bar with fade animation
        fade_effect = QGraphicsOpacityEffect(self.progress_bar)
        self.progress_bar.setGraphicsEffect(fade_effect)
        
        fade_animation = QPropertyAnimation(fade_effect, b"opacity")
        fade_animation.setDuration(1000)
        fade_animation.setStartValue(1.0)
        fade_animation.setEndValue(0.0)
        fade_animation.finished.connect(self.progress_bar.deleteLater)
        fade_animation.start()
        
        self.show_info("Filling completed successfully!")
        self.status_bar.showMessage("Ready")
        
    def update_water_quality(self, ph, tds):
        self.ph_value.setText(f"{ph:.1f}")
        self.tds_value.setText(f"{tds} ppm")
        
        # Update color based on values
        if 6.5 <= ph <= 8.5:
            self.ph_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #27AE60;")
        else:
            self.ph_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #E74C3C;")
            
        if 0 <= tds <= 100:
            self.tds_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #27AE60;")
        else:
            self.tds_value.setStyleSheet("font-size: 24px; font-weight: bold; color: #E74C3C;")
        
    def closeEvent(self, event):
        try:
            # Stop all running processes
            self.sensor_thread.stop()
            self.sensor_thread.wait()
            self.stop_filling_sound()
            self.media_player.stop()
            
            # Save window state
            self.settings.setValue('geometry', self.saveGeometry())
            
            # Clean up resources
            self.tray_icon.hide()
            super().closeEvent(event)
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")
            event.accept()

def exception_hook(exctype, value, traceback):
    logging.error("Uncaught exception", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

if __name__ == '__main__':
    try:
        # Set exception hook
        sys.excepthook = exception_hook
        
        # Create application
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create and show main window
        window = WaterVendingMachine()
        window.show()
        
        # Start application event loop
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Application failed to start: {str(e)}")
        raise