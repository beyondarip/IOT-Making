import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
                           QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont
import random
import os

class WaterButton(QPushButton):
    def __init__(self, size_text, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
        self.setCheckable(True)
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Container untuk gambar
        icon_container = QLabel()
        icon_container.setFixedSize(100, 100)
        icon_container.setStyleSheet("background-color: white; border-radius: 10px;")
        
        # Load dan set gambar bottle
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_container.setPixmap(scaled_pixmap)
        icon_container.setAlignment(Qt.AlignCenter)
        
        # Label untuk ukuran
        size_label = QLabel(size_text)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")
        
        layout.addWidget(icon_container, alignment=Qt.AlignCenter)
        layout.addWidget(size_label, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
            WaterButton {
                background-color: #E6F3FF;
                border-radius: 20px;
                border: 2px solid #B3D9FF;
            }
            WaterButton:checked {
                background-color: #80BFFF;
                border: 2px solid #3399FF;
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
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Progress bar container
        progress_container = QWidget()
        progress_container.setStyleSheet("""
            background-color: #4F5D75;
            border-radius: 15px;
            padding: 10px;
            margin: 5px;
        """)
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        
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
            padding: 10px;
            margin: 5px;
        """)
        machine_layout = QVBoxLayout(machine_display)
        machine_layout.setSpacing(5)
        machine_layout.setContentsMargins(10, 5, 10, 5)
        
        # Container untuk gambar mesin
        self.machine_image = QLabel()
        self.machine_image.setFixedSize(150, 150)
        self.machine_image.setAlignment(Qt.AlignCenter)
        
        # Load gambar mesin
        machine_pixmap = QPixmap("5.png")
        scaled_machine = machine_pixmap.scaled(
            130, 130,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.machine_image.setPixmap(scaled_machine)
        
        # Start Filling Button
        self.start_button = QPushButton("Start Filling")
        self.start_button.setFixedSize(120, 50)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 5px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                margin: 0px;
                padding: 0px;
                margin-top: 20px;
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
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Title
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        
        # Monitoring container
        monitor_container = QWidget()
        monitor_container.setStyleSheet("""
            background-color: #E6F3FF;
            border-radius: 15px;
            padding: 10px;
        """)
        monitor_layout = QHBoxLayout(monitor_container)
        monitor_layout.setContentsMargins(10, 5, 10, 5)
        
        # pH Value
        ph_widget = QWidget()
        ph_layout = QVBoxLayout(ph_widget)
        ph_layout.setSpacing(5)
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
        tds_layout.setSpacing(5)
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
        
        self.selected_size = None
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Innovative Aqua Solution")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin: 10px;
        """)
        
        # Content layout
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Left panel - Video display
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Video container
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            background-color: #E6F3FF;
            border-radius: 15px;
            padding: 10px;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        
        # Video title
        video_title = QLabel("Video Display For Campaign Water Sustainability")
        video_title.setAlignment(Qt.AlignCenter)
        video_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 5px;")
        
        left_layout.addWidget(video_title)
        left_layout.addWidget(self.video_label)
        left_layout.addWidget(MonitoringWidget())
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        
        # Water size selection
        sizes_widget = QWidget()
        sizes_widget.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 5px;
        """)
        sizes_layout = QVBoxLayout(sizes_widget)
        sizes_layout.setSpacing(5)
        sizes_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title for water sizes
        sizes_title = QLabel("Pilihan Ukuran Air")
        sizes_title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 5px;")
        sizes_layout.addWidget(sizes_title)
        
        # Grid for water buttons
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        water_sizes = [
            ("100 ml", "1.png", 0, 0),
            ("350 ml", "2.png", 0, 1),
            ("600 ml", "3.png", 1, 0),
            ("1 Liter", "4.png", 1, 1)
        ]
        
        self.size_buttons = []
        for size, image_path, row, col in water_sizes:
            btn = WaterButton(size, image_path)
            btn.clicked.connect(lambda checked, s=size, b=btn: self.on_size_selected(s, b))
            buttons_grid.addWidget(btn, row, col)
            self.size_buttons.append(btn)
        
        sizes_layout.addLayout(buttons_grid)
        
        # Add machine widget
        self.machine_widget = MachineWidget()
        self.machine_widget.start_button.clicked.connect(self.start_filling)
        sizes_layout.addWidget(self.machine_widget)
        
        right_layout.addWidget(sizes_widget)
        
        # Add panels to content layout
        content.addWidget(left_panel, 60)
        content.addWidget(right_panel, 40)
        
        # Add all elements to main layout
        layout.addWidget(header)
        layout.addLayout(content)
        
        # Setup video
        self.setup_video()
        self.setup_sensor_updates()
    
    def on_size_selected(self, size, clicked_button):
        for btn in self.size_buttons:
            if btn != clicked_button:
                btn.setChecked(False)
        
        self.selected_size = size if clicked_button.isChecked() else None
        self.machine_widget.start_button.setEnabled(self.selected_size is not None)
    
    def start_filling(self):
        if self.selected_size:
            print(f"Starting filling process for {self.selected_size}")
    
    def setup_video(self):
        video_path = "yqq.mp4"
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print("Error: Could not open video file")
            return
            
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_frame)
        self.video_timer.start(33)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            if frame is None:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            scaled_pixmap = QPixmap.fromImage(image).scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.video_label.setPixmap(scaled_pixmap)
    
    def setup_sensor_updates(self):
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_values)
        self.sensor_timer.start(2000)
    
    def update_sensor_values(self):
        ph = round(random.uniform(8.0, 8.4), 1)
        self.findChild(MonitoringWidget).ph_value.setText(f"{ph}")
        
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