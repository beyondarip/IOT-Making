import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
                           QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import random

class WaterButton(QPushButton):
    def __init__(self, size_text, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Container untuk gambar
        icon_container = QWidget()
        icon_container.setFixedSize(100, 100)
        icon_container.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
        """)
        
        # Label untuk ukuran
        size_label = QLabel(size_text)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("""
            color: black;
            font-size: 16px;
            font-weight: bold;
        """)
        
        layout.addWidget(icon_container, alignment=Qt.AlignCenter)
        layout.addWidget(size_label, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
            WaterButton {
                background-color: #E6F3FF;
                border-radius: 20px;
                border: 2px solid #B3D9FF;
            }
            WaterButton:hover {
                background-color: #B3D9FF;
                border: 2px solid #80BFFF;
            }
        """)

class MachineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(250)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)
        
        # Progress bar container
        progress_container = QWidget()
        progress_container.setStyleSheet("""
            background-color: #4F5D75;
            border-radius: 15px;
        """)
        progress_layout = QHBoxLayout(progress_container)
        
        # Progress indicators
        self.progress_indicator = QLabel("●")
        self.progress_indicator.setStyleSheet("color: #2ECC71; font-size: 24px;")
        self.progress_bar = QLabel("▬" * 15)
        self.progress_bar.setStyleSheet("color: white; font-size: 16px;")
        
        progress_layout.addWidget(self.progress_indicator)
        progress_layout.addWidget(self.progress_bar, 1)
        
        # Machine display
        machine_display = QWidget()
        machine_display.setStyleSheet("""
            background-color: #4F5D75;
            border-radius: 15px;
        """)
        machine_layout = QVBoxLayout(machine_display)
        
        # Bottle visualization
        self.bottle_widget = QWidget()
        self.bottle_widget.setFixedSize(100, 150)
        self.bottle_widget.setStyleSheet("""
            background-color: #2ECC71;
            border-radius: 10px;
        """)
        
        machine_layout.addWidget(self.bottle_widget, alignment=Qt.AlignCenter)
        
        layout.addWidget(progress_container)
        layout.addWidget(machine_display)

class MonitoringWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: black;
        """)
        
        # Monitoring container
        monitor_container = QWidget()
        monitor_container.setStyleSheet("""
            background-color: #E6F3FF;
            border-radius: 15px;
            padding: 15px;
        """)
        monitor_layout = QHBoxLayout(monitor_container)
        
        # pH Value
        ph_widget = QWidget()
        ph_layout = QVBoxLayout(ph_widget)
        ph_title = QLabel("pH Value")
        self.ph_value = QLabel("8.2")
        ph_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.ph_value.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
        """)
        ph_layout.addWidget(ph_title)
        ph_layout.addWidget(self.ph_value)
        
        # TDS Value
        tds_widget = QWidget()
        tds_layout = QVBoxLayout(tds_widget)
        tds_title = QLabel("TDS Value:")
        self.tds_value = QLabel("8 ppm")
        tds_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.tds_value.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
        """)
        tds_layout.addWidget(tds_title)
        tds_layout.addWidget(self.tds_value)
        
        monitor_layout.addWidget(ph_widget)
        monitor_layout.addWidget(tds_widget)
        
        layout.addWidget(title)
        layout.addWidget(monitor_container)

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("background-color: #40E0D0;")
        self.setMinimumSize(1200, 800)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Innovative Aqua Solution")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin: 20px;
        """)
        
        # Content layout
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Left panel - Video display
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video container
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            background-color: #E6F3FF;
            border-radius: 15px;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        
        # Video title
        video_title = QLabel("Video Display For Campaign Water Sustainability")
        video_title.setAlignment(Qt.AlignCenter)
        video_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin: 10px;
        """)
        
        left_layout.addWidget(video_title)
        left_layout.addWidget(self.video_label)
        left_layout.addWidget(MonitoringWidget())
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Water size selection
        sizes_widget = QWidget()
        sizes_widget.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 20px;
        """)
        sizes_layout = QVBoxLayout(sizes_widget)
        
        # Title for water sizes
        sizes_title = QLabel("Pilihan Ukuran Air")
        sizes_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        sizes_layout.addWidget(sizes_title)
        
        # Grid for water buttons
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        water_sizes = [
            ("100 ml", 0, 0),
            ("350 ml", 0, 1),
            ("600 ml", 1, 0),
            ("1 Liter", 1, 1)
        ]
        
        for size, row, col in water_sizes:
            btn = WaterButton(size)
            btn.clicked.connect(lambda checked, s=size: self.on_size_selected(s))
            buttons_grid.addWidget(btn, row, col)
        
        sizes_layout.addLayout(buttons_grid)
        
        # Add machine widget
        self.machine_widget = MachineWidget()
        sizes_layout.addWidget(self.machine_widget)
        
        right_layout.addWidget(sizes_widget)
        
        # Add panels to content layout
        content.addWidget(left_panel, 60)
        content.addWidget(right_panel, 40)
        
        # Add all elements to main layout
        layout.addWidget(header)
        layout.addLayout(content)
        
        # Setup timers
        self.setup_video()
        self.setup_sensor_updates()
    
    def on_size_selected(self, size):
        print(f"Selected water size: {size}")
    
    def setup_video(self):
        self.cap = cv2.VideoCapture(0)  # Use 0 for webcam or provide video file path
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_frame)
        self.video_timer.start(33)  # ~30 FPS
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_pixmap = QPixmap.fromImage(image).scaled(
                self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)
    
    def setup_sensor_updates(self):
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_values)
        self.sensor_timer.start(2000)
    
    def update_sensor_values(self):
        # Update pH value (8.0 - 8.4)
        ph = round(random.uniform(8.0, 8.4), 1)
        self.findChild(MonitoringWidget).ph_value.setText(f"{ph}")
        
        # Update TDS value (6-10 ppm)
        tds = random.randint(6, 10)
        self.findChild(MonitoringWidget).tds_value.setText(f"{tds} ppm")
    
    def closeEvent(self, event):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterSustainabilityApp()
    window.show()
    sys.exit(app.exec_())