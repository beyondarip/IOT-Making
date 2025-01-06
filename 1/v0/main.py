import sys
import os
import math
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
                           QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                           QProgressBar, QMessageBox, QSplashScreen)
from PyQt5.QtCore import (Qt, QTimer, QSize, QUrl, pyqtSignal, QPropertyAnimation,
                         QEasingCurve, QRect, QPoint, pyqtProperty)
from PyQt5.QtGui import (QColor, QPalette, QFont, QIcon, QPixmap, QPainter, 
                        QPainterPath, QLinearGradient)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
import random

class WaterSizeButton(QPushButton):
    def __init__(self, size, volume, parent=None):
        super().__init__(parent)
        self.size = size
        self.volume = volume
        self.is_selected = False
        self.image_loaded = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the button UI"""
        self.setFixedSize(150, 150)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_stylesheet()
        self.load_image()
        
    def setup_stylesheet(self):
        """Setup the button stylesheet"""
        self.setStyleSheet("""
            WaterSizeButton {
                border: 2px solid #40E0D0;
                border-radius: 15px;
                padding: 10px;
                background-color: white;
            }
            WaterSizeButton:checked {
                background-color: #E0FFFF;
                border: 3px solid #20B2AA;
            }
            WaterSizeButton:hover {
                background-color: #F0FFFF;
            }
        """)
        
    def load_image(self):
        """Load bottle image or fallback to emoji"""
        image_paths = {
            '100ml': 'assets/bottle_100ml.png',
            '350ml': 'assets/bottle_350ml.png',
            '600ml': 'assets/bottle_600ml.png',
            '1 Liter': 'assets/bottle_1l.png'
        }
        
        if self.size in image_paths and os.path.exists(image_paths[self.size]):
            pixmap = QPixmap(image_paths[self.size])
            scaled_pixmap = pixmap.scaled(80, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setIcon(QIcon(scaled_pixmap))
            self.setIconSize(QSize(80, 120))
            self.image_loaded = True
        else:
            self.setup_fallback_display()
    
    def setup_fallback_display(self):
        """Setup fallback display with emoji and text"""
        self.setText(f"🍶\n{self.size}")
        self.setFont(QFont('Segoe UI', 12))

class WaterSizeSelector(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.selected_size = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the water size selector UI"""
        self.setStyleSheet("""
            WaterSizeSelector {
                background-color: #E0FFFF;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Pilihan Ukuran Air")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2F4F4F;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Grid for bottle size buttons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        # Create size buttons
        sizes = [
            ('100ml', '100'),
            ('350ml', '350'),
            ('600ml', '600'),
            ('1 Liter', '1000')
        ]
        
        for idx, (size_label, volume) in enumerate(sizes):
            btn = WaterSizeButton(size_label, volume)
            btn.clicked.connect(lambda checked, b=btn: self.handle_button_click(b))
            self.buttons.append(btn)
            grid_layout.addWidget(btn, idx // 2, idx % 2, Qt.AlignCenter)
        
        layout.addLayout(grid_layout)
        
        # Add information label
        info_label = QLabel("Pilih ukuran air terlebih dahulu")
        info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-style: italic;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
    def handle_button_click(self, clicked_button):
        """Handle button click events"""
        for button in self.buttons:
            if button != clicked_button:
                button.setChecked(False)
        
        if clicked_button.isChecked():
            self.selected_size = clicked_button.volume
        else:
            self.selected_size = None
            
        # Emit signal or call callback for parent widget
        self.size_selected(self.selected_size)
        
    def size_selected(self, volume):
        """Callback for when a size is selected"""
        pass

    def reset_selection(self):
        """Reset all buttons to unselected state"""
        for button in self.buttons:
            button.setChecked(False)
        self.selected_size = None

class VideoPlayer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_video_player()
        
    def init_ui(self):
        """Initialize the video player UI"""
        self.setStyleSheet("""
            VideoPlayer {
                background-color: #F0FFFF;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.layout.addWidget(self.video_widget)
        
        # Error label (hidden by default)
        self.error_label = QLabel("Video tidak dapat dimuat")
        self.error_label.setStyleSheet("""
            QLabel {
                color: #FF6B6B;
                background-color: #FFE5E5;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        self.layout.addWidget(self.error_label)
        
    def setup_video_player(self):
        """Setup the video player and media content"""
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        print(f"Media Player State: {self.media_player.state()}")
        print(f"Video Output Status: {self.media_player.availability()}")

        self.media_player.error.connect(self.handle_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        self.media_player.stateChanged.connect(lambda state: print(f"Player State Changed: {state}"))
    
        # Load video
        self.load_video()
        
    def load_video(self):
        """Load and play the video file"""
        # Pastikan path video relatif terhadap lokasi script
        video_path = Path(__file__).parent / "assets" / "video.mp4"
        
        try:
            if video_path.exists():
                url = QUrl.fromLocalFile(str(video_path))
                self.media_player.setMedia(QMediaContent(url))
                self.media_player.play()
                self.media_player.mediaStatusChanged.connect(self.loop_video)
            else:
                print(f"Video file not found at {video_path}")
                raise FileNotFoundError("Video file not found")
        except Exception as e:
            self.handle_error(str(e))
            print(f"Error loading video: {str(e)}")
            
    def loop_video(self, status):
        """Loop the video when it ends"""
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
            
    def handle_error(self, error):
        """Handle video player errors"""
        self.error_label.show()
        self.video_widget.hide()
        print(f"Video player error: {error}")
        
    def handle_media_status(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.LoadedMedia:
            self.error_label.hide()
            self.video_widget.show()

class WaterQualityMonitor(QFrame):
    # Signals for value changes
    ph_changed = pyqtSignal(float)
    tds_changed = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ph_value = 8.2
        self.tds_value = 8.0
        self.init_ui()
        self.setup_monitoring()
        
    def init_ui(self):
        """Initialize the water quality monitor UI"""
        self.setStyleSheet("""
            WaterQualityMonitor {
                background-color: #20B2AA;
                border-radius: 15px;
                padding: 15px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            .value-label {
                background-color: white;
                color: #2F4F4F;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        layout = QGridLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title, 0, 0, 1, 2, Qt.AlignCenter)
        
        # pH Value
        self.ph_label = QLabel("pH Value:")
        self.ph_display = QLabel(f"{self.ph_value:.1f}")
        self.ph_display.setProperty("class", "value-label")
        
        # TDS Value
        self.tds_label = QLabel("TDS Value:")
        self.tds_display = QLabel(f"{self.tds_value:.1f} ppm")
        self.tds_display.setProperty("class", "value-label")
        
        # Add widgets to layout
        layout.addWidget(self.ph_label, 1, 0)
        layout.addWidget(self.ph_display, 1, 1)
        layout.addWidget(self.tds_label, 2, 0)
        layout.addWidget(self.tds_display, 2, 1)
        
        # Add quality indicators
        self.setup_quality_indicators()
        
    def setup_quality_indicators(self):
        """Setup quality status indicators"""
        self.ph_indicator = QLabel("🟢 Normal")
        self.tds_indicator = QLabel("🟢 Excellent")
        
        self.ph_indicator.setStyleSheet("color: #98FF98;")
        self.tds_indicator.setStyleSheet("color: #98FF98;")
        
        layout = self.layout()
        layout.addWidget(self.ph_indicator, 1, 2)
        layout.addWidget(self.tds_indicator, 2, 2)
        
    def setup_monitoring(self):
        """Setup real-time monitoring simulation"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_values)
        self.update_timer.start(2000)  # Update every 2 seconds
        
    def update_values(self):
        """Update pH and TDS values with realistic variations"""
        self.ph_value += random.uniform(-0.1, 0.1)
        self.ph_value = max(6.5, min(8.5, self.ph_value))
        
        self.tds_value += random.uniform(-0.5, 0.5)
        self.tds_value = max(5.0, min(12.0, self.tds_value))
        
        # Update displays
        self.ph_display.setText(f"{self.ph_value:.1f}")
        self.tds_display.setText(f"{self.tds_value:.1f} ppm")
        
        # Update indicators
        self.update_indicators()
        
        # Emit signals
        self.ph_changed.emit(self.ph_value)
        self.tds_changed.emit(self.tds_value)
        
    def update_indicators(self):
        """Update quality status indicators"""
        if 6.8 <= self.ph_value <= 7.8:
            self.ph_indicator.setText("🟢 Normal")
            self.ph_indicator.setStyleSheet("color: #98FF98;")
        else:
            self.ph_indicator.setText("🟡 Warning")
            self.ph_indicator.setStyleSheet("color: #FFD700;")
            
        if self.tds_value <= 10:
            self.tds_indicator.setText("🟢 Excellent")
            self.tds_indicator.setStyleSheet("color: #98FF98;")
        else:
            self.tds_indicator.setText("🟡 Good")
            self.tds_indicator.setStyleSheet("color: #FFD700;")

class WaterWaveEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._water_level = 0
        self._wave_offset = 0
        self.wave_anim = QTimer()
        self.wave_anim.timeout.connect(self.update_wave)
        self.wave_anim.start(50)
        self.water_color = QColor(64, 164, 223, 180)
        
    def update_wave(self):
        """Update wave animation offset"""
        self._wave_offset += 5
        if self._wave_offset >= 360:
            self._wave_offset = 0
        self.update()
        
    def set_water_level(self, level):
        """Set water fill level (0-100)"""
        self._water_level = max(0, min(100, level))
        self.update()
        
    def get_water_level(self):
        return self._water_level
        
    water_level = pyqtProperty(float, get_water_level, set_water_level)
    
    def paintEvent(self, event):
        """Custom paint event for water wave effect"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create container path
        container = QPainterPath()
        container.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # Calculate water height based on level
        water_height = int(self.height() * (self._water_level / 100))
        water_y = self.height() - water_height
        
        # Create water path with wave effect
        water = QPainterPath()
        water.moveTo(0, self.height())
        
        # Generate wave points
        wave_height = 10
        for x in range(0, self.width(), 5):
            y = water_y + math.sin((x + self._wave_offset) * 0.05) * wave_height
            water.lineTo(x, y)
            
        water.lineTo(self.width(), self.height())
        water.lineTo(0, self.height())
        
        # Create gradient for water
        gradient = QLinearGradient(0, water_y, 0, self.height())
        gradient.setColorAt(0, self.water_color.lighter(130))
        gradient.setColorAt(1, self.water_color)
        
        # Draw container
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(240, 240, 240))
        painter.drawPath(container)
        
        # Draw water
        painter.setBrush(gradient)
        painter.drawPath(water)

class WaterFillingAnimation(QFrame):
    filling_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize water filling animation UI"""
        self.setStyleSheet("""
            WaterFillingAnimation {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #40E0D0;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Water wave effect widget
        self.water_effect = WaterWaveEffect(self)
        layout.addWidget(self.water_effect)
        
        # Progress information
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2F4F4F;
            }
        """)
        layout.addWidget(self.progress_label)
        
        # Setup animation
        self.fill_animation = QPropertyAnimation(self.water_effect, b"water_level")
        self.fill_animation.setDuration(3000)  # 3 seconds
        self.fill_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fill_animation.valueChanged.connect(self.update_progress_label)
        self.fill_animation.finished.connect(self.filling_complete)
        
    def start_filling(self, volume):
        """Start water filling animation"""
        self.fill_animation.setStartValue(0)
        self.fill_animation.setEndValue(100)
        self.fill_animation.start()
        
    def update_progress_label(self, value):
        """Update progress label during animation"""
        self.progress_label.setText(f"{int(value)}%")

class FillingProcess(QFrame):
    process_complete = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_volume = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize filling process UI"""
        self.setStyleSheet("""
            FillingProcess {
                background-color: #E0FFFF;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Siap untuk mengisi")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2F4F4F;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Filling animation
        self.filling_animation = WaterFillingAnimation()
        self.filling_animation.filling_complete.connect(self.handle_filling_complete)
        layout.addWidget(self.filling_animation)
        
        # Volume info
        self.volume_label = QLabel()
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666666;
            }
        """)
        layout.addWidget(self.volume_label)
        
    def start_filling(self, volume):
        """Start the filling process"""
        self.current_volume = volume
        self.status_label.setText("Sedang Mengisi...")
        self.volume_label.setText(f"Volume: {volume}ml")
        self.filling_animation.start_filling(volume)
        
    def handle_filling_complete(self):
        """Handle completion of filling process"""
        self.status_label.setText("Pengisian Selesai!")
        QTimer.singleShot(2000, self.reset_state)
        self.process_complete.emit()
        
    def reset_state(self):
        """Reset to initial state"""
        self.status_label.setText("Siap untuk mengisi")
        self.volume_label.setText("")
        self.current_volume = None

class WaterVendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_system()
        self.show_splash_screen()
        QTimer.singleShot(2000, self.init_ui)  # Show splash for 2 seconds
        
    def init_system(self):
        """Initialize system variables and states"""
        self.is_filling = False
        self.current_volume = None
        self.system_ready = True
        self.maintenance_mode = False
        
    def show_splash_screen(self):
        """Show splash screen during initialization"""
        splash_pixmap = QPixmap("assets/splash.png")
        if not splash_pixmap.isNull():
            splash = QSplashScreen(splash_pixmap)
        else:
            # Fallback splash screen
            splash = QSplashScreen(QPixmap(400, 300))
            # splash.fill(QColor("#40E0D0"))
            
        splash.show()
        splash.showMessage("Loading Innovative Aqua Solution...", 
                         Qt.AlignCenter | Qt.AlignBottom,
                         Qt.white)
        QApplication.processEvents()

    def init_ui(self):
        """Initialize the main user interface"""
        # Set window properties
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #40E0D0;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create header
        self.setup_header()
        
        # Create content layout
        content_layout = QHBoxLayout()
        
        # Left section (Video and Water Quality)
        left_section = self.create_left_section()
        content_layout.addWidget(left_section, 2)
        
        # Right section (Water Size Selection and Filling)
        right_section = self.create_right_section()
        content_layout.addWidget(right_section, 1)
        
        main_layout.addLayout(content_layout)
        
        # Add status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #20B2AA;
                color: white;
            }
        """)
        self.update_status("System Ready")
        
        # Set window to be responsive
        self.setMinimumSize(800, 600)
        
        # Connect components
        self.setup_connections()
        
    def setup_header(self):
        """Setup the header section"""
        header = QLabel("Innovative Aqua Solution")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 10px;
                background-color: #20B2AA;
                border-radius: 10px;
            }
        """)
        self.centralWidget().layout().addWidget(header)
        
    def create_left_section(self):
        """Create the left section with video and water quality"""
        left_widget = QFrame()
        left_widget.setStyleSheet("""
            QFrame {
                background-color: #E0FFFF;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(left_widget)
        
        # Add video player
        self.video_player = VideoPlayer()
        layout.addWidget(self.video_player)
        
        # Add water quality monitor
        self.water_quality_monitor = WaterQualityMonitor()
        layout.addWidget(self.water_quality_monitor)
        
        return left_widget
        
    def create_right_section(self):
        """Create the right section with water size selector"""
        right_widget = QFrame()
        layout = QVBoxLayout(right_widget)
        
        # Add water size selector
        self.size_selector = WaterSizeSelector()
        layout.addWidget(self.size_selector)
        
        # Add filling process
        self.filling_process = FillingProcess()
        layout.addWidget(self.filling_process)
        
        return right_widget
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Water quality monitoring connections
        self.water_quality_monitor.ph_changed.connect(self.handle_ph_change)
        self.water_quality_monitor.tds_changed.connect(self.handle_tds_change)
        
        # Size selector connections
        self.size_selector.size_selected = self.handle_size_selection
        
        # Filling process connections
        self.filling_process.process_complete.connect(self.handle_filling_complete)
        
    def handle_ph_change(self, value):
        """Handle pH value changes"""
        if value < 6.5 or value > 8.5:
            self.show_warning("Water Quality Warning",
                            f"pH level ({value:.1f}) is outside safe range!")
            self.system_ready = False
        else:
            self.system_ready = True
            
    def handle_tds_change(self, value):
        """Handle TDS value changes"""
        if value > 15:
            self.show_warning("Water Quality Warning",
                            f"TDS level ({value:.1f} ppm) is too high!")
            self.system_ready = False
        else:
            self.system_ready = True
            
    def show_warning(self, title, message):
        """Show warning message box"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QPushButton {
                padding: 5px 20px;
                background-color: #40E0D0;
                border: none;
                border-radius: 5px;
                color: white;
            }
        """)
        msg.exec_()
        
    def handle_size_selection(self, volume):
        """Handle water size selection"""
        if not self.system_ready:
            self.show_warning("System Not Ready",
                            "Please wait for water quality to normalize.")
            return
            
        if self.is_filling:
            return
            
        if volume:
            self.current_volume = volume
            self.start_filling_process()
            
    def start_filling_process(self):
        """Start the water filling process"""
        self.is_filling = True
        self.update_status(f"Filling {self.current_volume}ml of water...")
        self.filling_process.start_filling(self.current_volume)
        
    def handle_filling_complete(self):
        """Handle completion of filling process"""
        self.is_filling = False
        self.current_volume = None
        self.update_status("Fill complete! Ready for next order.")
        self.size_selector.reset_selection()
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)
        
    def closeEvent(self, event):
        """Handle application closing"""
        if self.is_filling:
            reply = QMessageBox.question(self, 'Exit Confirmation',
                                       'A filling process is in progress. Are you sure you want to exit?',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.cleanup_system()
                event.accept()
            else:
                event.ignore()
        else:
            self.cleanup_system()
            event.accept()
            
    def cleanup_system(self):
        """Cleanup system resources before exit"""
        # Stop all timers
        self.water_quality_monitor.update_timer.stop()
        
        # Stop video playback
        self.video_player.media_player.stop()
        
        # Reset system state
        self.system_ready = False
        self.is_filling = False
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        # Maintenance mode toggle (Ctrl + M)
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_M:
            self.maintenance_mode = not self.maintenance_mode
            self.update_status("Maintenance Mode: " + 
                             ("Enabled" if self.maintenance_mode else "Disabled"))
            
        # Emergency stop (Esc)
        elif event.key() == Qt.Key_Escape and self.is_filling:
            self.emergency_stop()
            
    def emergency_stop(self):
        """Handle emergency stop"""
        if self.is_filling:
            self.is_filling = False
            self.filling_process.reset_state()
            self.update_status("Emergency Stop Activated!")
            self.show_warning("Emergency Stop",
                            "Filling process has been stopped.")

def main():
    try:
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        app.setFont(QFont('Segoe UI', 10))
        
        # Create and show main window
        window = WaterVendingMachine()
        window.show()
        window.showMaximized()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()