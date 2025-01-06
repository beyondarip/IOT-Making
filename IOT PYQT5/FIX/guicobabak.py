import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import random
import os
import gc

# Thread untuk video processing
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self._setup_video()
        
    def _setup_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        # Set resolusi rendah
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # Set buffer kecil
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Reset video jika sudah selesai
                if frame is None:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                    
                # Kurangi ukuran frame
                frame = cv2.resize(frame, (320, 240))
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(image)
            
            # Delay untuk mengurangi CPU usage
            self.msleep(100)  # 10 FPS
            
        self.cap.release()
        
    def stop(self):
        self.running = False
        self.wait()

class WaterButton(QPushButton):
    def __init__(self, size_text, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.setCheckable(True)
        self.setText(size_text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #E6F3FF;
                border: 2px solid #B3D9FF;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #80BFFF;
                border: 2px solid #3399FF;
            }
        """)

class MachineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(200)
        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Progress indicator (simplified)
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("font-size: 16px;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        # Start Button
        self.start_button = QPushButton("Start Filling")
        self.start_button.setFixedSize(120, 40)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #95A5A6;
            }
        """)
        
        layout.addWidget(self.progress_label)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

class MonitoringWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # pH Value
        ph_widget = QWidget()
        ph_layout = QVBoxLayout(ph_widget)
        self.ph_value = QLabel("8.2")
        self.ph_value.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.ph_value.setAlignment(Qt.AlignCenter)
        ph_layout.addWidget(QLabel("pH Value"))
        ph_layout.addWidget(self.ph_value)
        
        # TDS Value
        tds_widget = QWidget()
        tds_layout = QVBoxLayout(tds_widget)
        self.tds_value = QLabel("8 ppm")
        self.tds_value.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.tds_value.setAlignment(Qt.AlignCenter)
        tds_layout.addWidget(QLabel("TDS Value"))
        tds_layout.addWidget(self.tds_value)
        
        layout.addWidget(ph_widget)
        layout.addWidget(tds_widget)

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Innovative Aqua Solution")
        self.setMinimumSize(800, 600)  # Kurangi ukuran window
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel (Video dan Monitoring)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video label
        self.video_label = QLabel()
        self.video_label.setFixedSize(320, 240)  # Fixed size untuk optimasi
        
        # Monitoring widget
        self.monitoring = MonitoringWidget()
        
        left_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.monitoring)
        
        # Right panel (Control)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Water size buttons
        buttons_grid = QGridLayout()
        self.size_buttons = []
        sizes = ["100 ml", "350 ml", "600 ml", "1 Liter"]
        
        for i, size in enumerate(sizes):
            btn = WaterButton(size)
            btn.clicked.connect(lambda checked, s=size, b=btn: self.on_size_selected(s, b))
            buttons_grid.addWidget(btn, i//2, i%2)
            self.size_buttons.append(btn)
        
        # Machine widget
        self.machine_widget = MachineWidget()
        self.machine_widget.start_button.clicked.connect(self.start_filling)
        
        right_layout.addLayout(buttons_grid)
        right_layout.addWidget(self.machine_widget)
        right_layout.addStretch()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Setup video thread
        self.setup_video()
        self.setup_sensor_updates()
    
    def setup_video(self):
        video_path = "yqq.mp4"
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return
            
        self.thread = VideoThread(video_path)
        self.thread.change_pixmap_signal.connect(self.update_video)
        self.thread.start()
    
    def update_video(self, image):
        scaled_pixmap = QPixmap.fromImage(image).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
        gc.collect()  # Garbage collection
    
    def setup_sensor_updates(self):
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_values)
        self.sensor_timer.start(5000)  # Update setiap 5 detik
    
    def update_sensor_values(self):
        ph = round(random.uniform(8.0, 8.4), 1)
        self.monitoring.ph_value.setText(f"{ph}")
        tds = random.randint(6, 10)
        self.monitoring.tds_value.setText(f"{tds} ppm")
    
    def on_size_selected(self, size, clicked_button):
        for btn in self.size_buttons:
            if btn != clicked_button:
                btn.setChecked(False)
        self.machine_widget.start_button.setEnabled(clicked_button.isChecked())
    
    def start_filling(self):
        print("Starting filling process")
    
    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterSustainabilityApp()
    window.show()
    sys.exit(app.exec_())