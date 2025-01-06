import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
                           QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor
import random
import os
import requests
import json

class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        
    def run(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                return
                
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                    
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.frame_ready.emit(image)
                    
                except Exception as e:
                    print(f"Error processing video frame: {str(e)}")
                    continue
                    
                self.msleep(33)
                
            cap.release()
            
        except Exception as e:
            print(f"Error in video thread: {str(e)}")
        
    def stop(self):
        self.running = False

class SensorThread(QThread):
    sensor_updated = pyqtSignal(dict)
    
    def __init__(self, esp32_ip):
        super().__init__()
        self.esp32_ip = esp32_ip
        self.running = True
        
    def run(self):
        while self.running:
            try:
                response = requests.get(f"http://{self.esp32_ip}/data", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.sensor_updated.emit(data)
            except requests.exceptions.RequestException:
                self.sensor_updated.emit({'error': True})
            self.msleep(2000)
            
    def stop(self):
        self.running = False

class WaterButton(QPushButton):
    def __init__(self, size_text, image_path, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(150, 150)
        self.setCheckable(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Icon container
        icon_container = QLabel()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 5px;
        """)
        
        # Load and set bottle image
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_container.setPixmap(scaled_pixmap)
        icon_container.setAlignment(Qt.AlignCenter)
        
        # Size label
        size_label = QLabel(size_text)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        
        layout.addWidget(icon_container, alignment=Qt.AlignCenter)
        layout.addWidget(size_label, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
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
        """)

class MachineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Progress container
        progress_container = QWidget()
        progress_container.setStyleSheet("""
            background-color: #2C3E50;
            border-radius: 15px;
            padding: 10px;
        """)
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        
        self.progress_indicator = QLabel("●")
        self.progress_indicator.setStyleSheet("color: #2ECC71; font-size: 24px;")
        self.progress_bar = QLabel("▬" * 15)
        self.progress_bar.setStyleSheet("color: white; font-size: 16px;")
        
        progress_layout.addWidget(self.progress_indicator)
        progress_layout.addWidget(self.progress_bar, 1)
        
        # Machine display
        machine_display = QWidget()
        machine_display.setStyleSheet("""
            background-color: #2C3E50;
            border-radius: 15px;
            padding: 10px;
        """)
        machine_layout = QVBoxLayout(machine_display)
        machine_layout.setSpacing(5)
        machine_layout.setContentsMargins(10, 5, 10, 5)
        
        self.machine_image = QLabel()
        self.machine_image.setFixedSize(80, 80)
        self.machine_image.setAlignment(Qt.AlignCenter)
        self.machine_image.setStyleSheet("background: transparent;")
        
        # Check if machine image exists before loading
        if os.path.exists("5.png"):
            machine_pixmap = QPixmap("5.png")
            scaled_machine = machine_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.machine_image.setPixmap(scaled_machine)
        
        self.start_button = QPushButton("Start Filling")
        self.start_button.setFixedSize(150, 40)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                border: none;
            }
            QPushButton:disabled {
                background-color: #95A5A6;
            }
            QPushButton:hover:!disabled {
                background-color: #27AE60;
            }
        """)
        
        machine_layout.addWidget(self.machine_image, alignment=Qt.AlignCenter)
        machine_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        
        layout.addWidget(progress_container)
        layout.addWidget(machine_display)

class MonitoringWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(150)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(layout)
        
        self.esp32_ip = "192.168.137.117"
        
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            font-family: 'Segoe UI', Arial;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        monitor_container = QWidget()
        monitor_container.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 15px;
            border: 2px solid #E9ECEF;
            padding: 10px;
        """)
        monitor_layout = QHBoxLayout(monitor_container)
        monitor_layout.setContentsMargins(8, 4, 8, 4)
        
        # Initialize pH and TDS widgets first
        self.ph_widget = self.create_monitor_display("pH Value")
        self.tds_widget = self.create_monitor_display("TDS Value")
        
        monitor_layout.addWidget(self.ph_widget)
        monitor_layout.addWidget(self.tds_widget)
        
        layout.addWidget(title)
        layout.addWidget(monitor_container)
        
        # Initialize the sensor thread after widgets are created
        self.sensor_thread = SensorThread(self.esp32_ip)
        self.sensor_thread.sensor_updated.connect(self.update_sensor_display)
        self.sensor_thread.start()

    def create_monitor_display(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2C3E50;
            padding: 2px;
                                  
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Enable word wrap

        
        value_label = QLabel("Not Connected")
        value_label.setStyleSheet("""
            background-color: white;
            padding: 8px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            border: 1px solid #E9ECEF;
        """)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)  # Enable word wrap
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Store the value label as an attribute
        if title == "pH Value":
            self.ph_value = value_label
        else:
            self.tds_value = value_label
        
        return widget

    def update_sensor_display(self, data):
        if hasattr(self, 'ph_value') and hasattr(self, 'tds_value'):
            if 'error' in data:
                self.ph_value.setText("Not Connected")
                self.tds_value.setText("Not Connected")
            else:
                ph_value = data.get('ph', 'Error')
                self.ph_value.setText(f"{ph_value}")
                self.tds_value.setText(f"{ph_value}")  # Update with actual TDS value
        
    def closeEvent(self, event):
        if hasattr(self, 'sensor_thread'):
            self.sensor_thread.stop()
            self.sensor_thread.wait()
        super().closeEvent(event)

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("background-color: #E3F2FD;")
        
        # Get screen size
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.setMinimumSize(1366, 768)
        self.resize(width, height)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        # header = QLabel("Innovative Aqua Solution")
        # header.setStyleSheet("""
        #     font-size: 20px;
        #     font-weight: bold;
        #     color: #2C3E50;
        #     font-family: 'Segoe UI', Arial;
        #     padding: 5px;
        # """)
        # header.setAlignment(Qt.AlignCenter)
        
        # Content area
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Left panel (Video + Monitoring)
        left_panel = QWidget()
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # Video container
        video_container = QWidget()
        video_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        video_container.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 20px;
            border: 2px solid #E9ECEF;
            padding: 10px;
        """)
        video_layout = QVBoxLayout(video_container)
        
        self.video_label = QLabel()
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #E9ECEF; border-radius: 10px;")
        
        video_layout.addWidget(self.video_label)
        
        # Add video and monitoring to left panel
        left_layout.addWidget(video_container, 7)  # 70% of space
        left_layout.addWidget(MonitoringWidget(), 3)  # 30% of space
        
        # Right panel (Water selection + Machine)
        right_panel = QWidget()
        right_panel.setFixedWidth(350)  # Fixed width
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Water selection section
        selection_widget = QWidget()
        selection_widget.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 20px;
border: 2px solid #E9ECEF;
            padding: 20px;
        """)
        selection_layout = QVBoxLayout(selection_widget)
        
        # Title
        selection_title = QLabel("Select Water Size")
        selection_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            font-family: 'Segoe UI', Arial;
        """)
        selection_title.setAlignment(Qt.AlignCenter)
        
        # Buttons grid
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(10)
        
        water_sizes = [
            ("100 ml", "1.png", 0, 0),
            ("350 ml", "2.png", 0, 1),
            ("600 ml", "3.png", 1, 0),
            ("1 Liter", "4.png", 1, 1)
        ]
        
        self.size_buttons = []
        for size, image_path, row, col in water_sizes:
            if os.path.exists(image_path):
                btn = WaterButton(size, image_path)
                btn.clicked.connect(lambda checked, s=size, b=btn: self.on_size_selected(s, b))
                buttons_grid.addWidget(btn, row, col)
                self.size_buttons.append(btn)
        
        # Add components to selection layout
        selection_layout.addWidget(selection_title)
        selection_layout.addLayout(buttons_grid)
        selection_layout.addStretch()
        
        # Machine control widget
        self.machine_widget = MachineWidget()
        self.machine_widget.start_button.clicked.connect(self.start_filling)
        
        # Add all components to right panel
        right_layout.addWidget(selection_widget)
        right_layout.addWidget(self.machine_widget)
        right_layout.addStretch()
        
        # Add panels to content layout
        content_layout.addWidget(left_panel, 7)  # 70% width
        content_layout.addWidget(right_panel, 0)  # Fixed width
        
        # Add everything to main layout
        # main_layout.addWidget(header)
        main_layout.addWidget(content)
        
        # Setup video
        self.setup_video()
        
        self.selected_size = None

    def on_size_selected(self, size, clicked_button):
        """Handle water size selection"""
        for btn in self.size_buttons:
            if btn != clicked_button:
                btn.setChecked(False)
        
        self.selected_size = size if clicked_button.isChecked() else None
        self.machine_widget.start_button.setEnabled(self.selected_size is not None)

    def start_filling(self):
        """Handle start filling button click"""
        if self.selected_size:
            print(f"Starting filling process for {self.selected_size}")
            # Add actual filling process here

    def setup_video(self):
        """Setup video stream dengan better error handling"""
        video_path = "yqq.mp4"
        try:
            if not os.path.exists(video_path):
                self.video_label.setText("Video not found")
                return
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.video_label.setText("Could not open video")
                return
            
            cap.release()  # Test and release immediately
            
            self.video_thread = VideoThread(video_path)
            self.video_thread.frame_ready.connect(self.update_video_frame)
            self.video_thread.start()
            
        except Exception as e:
            self.video_label.setText(f"Error loading video: {str(e)}")

    def update_video_frame(self, image):
        """Update video frame dengan better error handling"""
        try:
            if self.video_label.size().isValid():
                scaled_pixmap = QPixmap.fromImage(image).scaled(
                    self.video_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.video_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error updating video frame: {str(e)}")

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        
        # Update video label minimum size while maintaining aspect ratio
        if hasattr(self, 'video_label'):
            new_width = min(640, int(self.width() * 0.4))
            new_height = min(480, int(self.height() * 0.4))
            self.video_label.setMinimumSize(new_width, new_height)

    def closeEvent(self, event):
        """Clean up resources when closing"""
        if hasattr(self, 'video_thread'):
            self.video_thread.stop()
            self.video_thread.wait()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont('Segoe UI', 10))
    
    # Create and show window
    window = WaterSustainabilityApp()
    window.show()
    
    sys.exit(app.exec_())