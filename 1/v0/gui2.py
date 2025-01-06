import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
                           QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QFont
import random

class WaterButton(QPushButton):
    def __init__(self, size_text, parent=None):
        super().__init__(parent)
        self.size_text = size_text
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QPushButton {
                background-color: #E6F3FF;
                border-radius: 15px;
                border: 2px solid #B3D9FF;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #B3D9FF;
                border: 2px solid #80BFFF;
            }
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bottle icon
        if self.size_text == "100 ml":
            # Draw glass icon
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#A0D8EF"))
            painter.drawRect(55, 40, 40, 50)
        else:
            # Draw bottle icon
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#A0D8EF"))
            painter.drawRoundedRect(55, 30, 40, 70, 5, 5)
            painter.drawRoundedRect(65, 20, 20, 15, 5, 5)
        
        # Draw size text
        painter.setPen(QColor("#333333"))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, self.size_text)

class MonitoringWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                padding: 15px;
            }
            QLabel {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        values_layout = QHBoxLayout()
        
        # pH Value
        self.ph_frame = QFrame()
        self.ph_frame.setStyleSheet("""
            QFrame {
                background-color: #E6F3FF;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        ph_layout = QVBoxLayout(self.ph_frame)
        self.ph_label = QLabel("pH Value")
        self.ph_value = QLabel("8.2")
        self.ph_value.setStyleSheet("color: #FF69B4; font-size: 24px;")
        ph_layout.addWidget(self.ph_label)
        ph_layout.addWidget(self.ph_value)
        
        # TDS Value
        self.tds_frame = QFrame()
        self.tds_frame.setStyleSheet("""
            QFrame {
                background-color: #E6F3FF;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        tds_layout = QVBoxLayout(self.tds_frame)
        self.tds_label = QLabel("TDS Value")
        self.tds_value = QLabel("8 ppm")
        self.tds_value.setStyleSheet("color: #FF69B4; font-size: 24px;")
        tds_layout.addWidget(self.tds_label)
        tds_layout.addWidget(self.tds_value)
        
        values_layout.addWidget(self.ph_frame)
        values_layout.addWidget(self.tds_frame)
        layout.addLayout(values_layout)

class MachineWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #4F5D75;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Progress indicator
        progress = QWidget()
        progress.setFixedHeight(30)
        progress.setStyleSheet("""
            background-color: #2D3748;
            border-radius: 15px;
        """)
        progress_layout = QHBoxLayout(progress)
        
        indicator = QLabel("●")
        indicator.setStyleSheet("color: #2ECC71; font-size: 20px;")
        progress_bar = QLabel("▬" * 8)
        progress_bar.setStyleSheet("color: #FFFFFF; font-size: 16px;")
        
        progress_layout.addWidget(indicator)
        progress_layout.addWidget(progress_bar)
        layout.addWidget(progress)
        
        # Machine visualization
        machine = QLabel()
        machine.setFixedSize(200, 200)
        machine.setStyleSheet("""
            background-color: #2D3748;
            border-radius: 10px;
        """)
        layout.addWidget(machine, alignment=Qt.AlignCenter)

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("background-color: #40E0D0;")
        self.setMinimumSize(1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Gambar logo Innovative Aqua Solution")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Main content layout
        content = QHBoxLayout()
        
        # Video display
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            background-color: #E6F3FF;
            border-radius: 15px;
            padding: 10px;
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        content.addWidget(self.video_label)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Water size selection
        sizes_widget = QFrame()
        sizes_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        sizes_layout = QVBoxLayout(sizes_widget)
        
        sizes_title = QLabel("Pilihan Ukuran Air")
        sizes_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        sizes_layout.addWidget(sizes_title)
        
        # Size buttons grid
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        sizes = ["100 ml", "350 ml", "600 ml", "1 Liter"]
        for i, size in enumerate(sizes):
            btn = WaterButton(size)
            buttons_grid.addWidget(btn, i // 2, i % 2)
        
        sizes_layout.addLayout(buttons_grid)
        
        # Add machine widget
        self.machine_widget = MachineWidget()
        sizes_layout.addWidget(self.machine_widget)
        
        right_layout.addWidget(sizes_widget)
        
        # Add monitoring widget
        self.monitoring = MonitoringWidget()
        right_layout.addWidget(self.monitoring)
        
        content.addWidget(right_panel)
        layout.addLayout(content)
        
        # Setup video and monitoring updates
        self.setup_video()
        self.setup_monitoring_updates()
    
    def setup_video(self):
        try:
            self.cap = cv2.VideoCapture('yqq.mp4')
            if not self.cap.isOpened():
                self.video_label.setText("Video Display For Campaign\nWater Sustainability")
                return
            
            self.video_timer = QTimer()
            self.video_timer.timeout.connect(self.update_frame)
            self.video_timer.start(33)
        except Exception as e:
            print(f"Video error: {str(e)}")
            self.video_label.setText("Video Display For Campaign\nWater Sustainability")
    
    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                if frame is None:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    return
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.video_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.video_label.setPixmap(scaled_pixmap)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        except Exception as e:
            print(f"Frame update error: {str(e)}")
    
    def setup_monitoring_updates(self):
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_monitoring)
        self.monitoring_timer.start(2000)
    
    def update_monitoring(self):
        ph = round(random.uniform(8.0, 8.4), 1)
        self.monitoring.ph_value.setText(f"{ph}")
        
        tds = random.randint(7, 9)
        self.monitoring.tds_value.setText(f"{tds} ppm")
    
    def closeEvent(self, event):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterSustainabilityApp()
    window.show()
    sys.exit(app.exec_())