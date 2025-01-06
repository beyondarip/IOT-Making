import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QImage, QPixmap
import random

class WaterFilling(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.water_level = 0
        self.is_filling = False
        
        # Timer untuk animasi
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_water_level)
        self.animation_timer.setInterval(50)  # Update setiap 50ms
        
    def paintEvent(self, event):
        if self.is_filling:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Gambar container
            container_rect = self.rect()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor('#2ECC71'))
            
            # Hitung tinggi air berdasarkan water_level (0-100)
            water_height = int((container_rect.height() * self.water_level) / 100)
            water_rect = QRect(
                container_rect.x(),
                container_rect.bottom() - water_height,
                container_rect.width(),
                water_height
            )
            painter.drawRect(water_rect)
    
    def start_filling(self):
        self.water_level = 0
        self.is_filling = True
        self.animation_timer.start()
    
    def update_water_level(self):
        if self.water_level < 100:
            self.water_level += 2  # Kecepatan pengisian
            self.update()
        else:
            self.animation_timer.stop()
            self.is_filling = False

class ProcessingUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Progress bar container
        progress_container = QWidget()
        progress_container.setFixedHeight(60)
        progress_container.setStyleSheet("""
            QWidget {
                background-color: #4F5D75;
                border-radius: 30px;
            }
        """)
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(20, 0, 20, 0)
        
        # LED indicator
        self.led = QLabel("⬤")
        self.led.setStyleSheet("color: #2ECC71; font-size: 12px;")
        progress_layout.addWidget(self.led)
        
        # Progress bar
        self.progress = QLabel()
        self.progress.setStyleSheet("background-color: white; border-radius: 2px;")
        self.progress.setFixedSize(80, 4)
        progress_layout.addWidget(self.progress)
        progress_layout.addStretch()
        
        # Processing unit container
        unit_container = QWidget()
        unit_container.setStyleSheet("""
            QWidget {
                background-color: #4F5D75;
                border-radius: 30px;
                padding: 15px;
            }
        """)
        unit_layout = QVBoxLayout(unit_container)
        
        # Water filling animation
        self.water_filling = WaterFilling()
        unit_layout.addWidget(self.water_filling)
        unit_layout.setContentsMargins(15, 15, 15, 15)
        
        layout.addWidget(progress_container)
        layout.addWidget(unit_container)
        layout.setContentsMargins(0, 0, 0, 0)
    
    def start_filling(self):
        self.water_filling.start_filling()

from PyQt5.QtCore import pyqtSignal

class WaterButton(QWidget):
    clicked = pyqtSignal()
    def __init__(self, size_text, icon_path, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container atas (gambar)
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        
        # Tambah gambar botol
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
        
        top_layout.addWidget(icon_label)
        
        top_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #B0E2FF;
                border-radius: 15px;
            }
        """)
        
        # Container bawah (text)
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        
        # Label untuk ukuran
        size_label = QLabel(size_text)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 14px;
                background-color: transparent;
            }
        """)
        
        bottom_layout.addWidget(size_label)
        bottom_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #B0E2FF;
                border-radius: 15px;
            }
        """)
        
        main_layout.addWidget(top_container)
        main_layout.addWidget(bottom_container)

        # Tambahkan mousePressEvent untuk handling klik
        self.mousePressEvent = lambda event: self.clicked.emit()

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("background-color: #40E0D0;")
        self.setMinimumSize(1200, 700)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Gambar logo Innovative Aqua Solution")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setStyleSheet("background-color: black; border-radius: 15px;")
        content_layout.addWidget(self.video_label)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Water size selection
        sizes_widget = QWidget()
        sizes_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        sizes_layout = QVBoxLayout(sizes_widget)
        
        title = QLabel("Pilihan Ukuran Air")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        sizes_layout.addWidget(title)
        
        # Grid for water buttons
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        # Define water sizes and their corresponding icons
        water_options = [
            ("100 ml", "1.png", 0, 0),
            ("350 ml", "2.png", 0, 1),
            ("600 ml", "3.png", 1, 0),
            ("1 Liter", "4.png", 1, 1)
        ]
        
        for size_text, icon_path, row, col in water_options:
            btn = WaterButton(size_text, icon_path)
            btn.clicked.connect(lambda s=size_text: self.on_size_selected(s))
            buttons_grid.addWidget(btn, row, col)
        
        sizes_layout.addLayout(buttons_grid)
        
        # Add processing unit
        self.processing_unit = ProcessingUnit()
        sizes_layout.addWidget(self.processing_unit)
        
        right_layout.addWidget(sizes_widget)
        
        # Monitoring section
        monitoring_widget = QWidget()
        monitoring_layout = QVBoxLayout(monitoring_widget)
        
        monitoring_title = QLabel("Water Quality Monitoring")
        monitoring_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        monitoring_layout.addWidget(monitoring_title)
        
        self.ph_label = QLabel("pH Value: 8.3")
        self.ph_label.setStyleSheet("""
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
        """)
        
        self.tds_label = QLabel("TDS Value: 9 ppm")
        self.tds_label.setStyleSheet("""
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
        """)
        
        monitoring_layout.addWidget(self.ph_label)
        monitoring_layout.addWidget(self.tds_label)
        
        right_layout.addWidget(monitoring_widget)
        content_layout.addWidget(right_panel)
        
        layout.addLayout(content_layout)
        
        # Setup video and sensors
        self.setup_video()
        self.setup_sensor_updates()
    
    def on_size_selected(self, size):
        print(f"Selected size: {size}")
        self.processing_unit.start_filling()
    
    def setup_video(self):
        try:
            self.cap = cv2.VideoCapture('yqq.mp4')
            if not self.cap.isOpened():
                raise Exception("Cannot open video")
            
            self.video_timer = QTimer()
            self.video_timer.timeout.connect(self.update_frame)
            self.video_timer.start(33)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.video_label.setText("")
    
    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                if frame is None:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_label.setPixmap(scaled_pixmap)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        except Exception as e:
            print(f"Error update frame: {str(e)}")
    
    def setup_sensor_updates(self):
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_values)
        self.sensor_timer.start(2000)
    
    def update_sensor_values(self):
        ph = round(random.uniform(8.0, 8.4), 1)
        self.ph_label.setText(f"pH Value: {ph}")
        tds = random.randint(6, 10)
        self.tds_label.setText(f"TDS Value: {tds} ppm")
    
    def closeEvent(self, event):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterSustainabilityApp()
    window.show()
    sys.exit(app.exec_())