import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
                           QPushButton, QStackedWidget)
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QSize
from PyQt5.QtSvg import QSvgWidget

class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QPushButton {
                background-color: #E6F3F7;
                border: 2px solid #86D0E9;
                border-radius: 15px;
                padding: 10px;
                color: #2C3E50;
            }
            QPushButton:hover {
                background-color: #BDE3F0;
                border: 2px solid #3498DB;
            }
            QPushButton:pressed {
                background-color: #A1D8E6;
            }
        """)

class WaterBottleWidget(QFrame):
    def __init__(self, volume, parent=None):
        super().__init__(parent)
        self.volume = volume
        self.selected = False
        self.initUI()

    def initUI(self):
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: #E6F3F7;
                border: 2px solid #86D0E9;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Create bottle icon SVG
        bottle_svg = f"""
        <svg viewBox="0 0 50 100">
            <path d="M20,10 L30,10 L32,20 C40,25 45,40 45,60 C45,85 35,95 25,95 C15,95 5,85 5,60 C5,40 10,25 18,20 Z"
                  fill="#BDE3F0" stroke="#3498DB" stroke-width="2"/>
            <rect x="22" y="0" width="6" height="10" fill="#BDE3F0" stroke="#3498DB" stroke-width="2"/>
        </svg>
        """
        
        bottle_widget = QSvgWidget()
        bottle_widget.setFixedSize(60, 80)
        bottle_widget.load(bytes(bottle_svg, 'utf-8'))
        
        volume_label = QLabel(self.volume)
        volume_label.setAlignment(Qt.AlignCenter)
        volume_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50;")
        
        layout.addWidget(bottle_widget, alignment=Qt.AlignCenter)
        layout.addWidget(volume_label, alignment=Qt.AlignCenter)
        
    def mousePressEvent(self, event):
        self.selected = not self.selected
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {'#BDE3F0' if self.selected else '#E6F3F7'};
                border: 2px solid {'#3498DB' if self.selected else '#86D0E9'};
                border-radius: 15px;
            }}
        """)
        super().mousePressEvent(event)

class MonitoringDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.startMonitoring()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #E6F3F7;
                border: 2px solid #86D0E9;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: #2C3E50;
                font-size: 14px;
            }
        """)
        
        layout = QHBoxLayout(self)
        
        # pH Value
        self.ph_value = QLabel("8.2")
        ph_label = QLabel("pH Value")
        ph_box = QFrame()
        ph_box.setStyleSheet("""
            QFrame {
                border: 1px solid #86D0E9;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        ph_layout = QHBoxLayout(ph_box)
        ph_layout.addWidget(ph_label)
        ph_layout.addWidget(self.ph_value)
        
        # TDS Value
        self.tds_value = QLabel("8 ppm")
        tds_label = QLabel("TDS Value:")
        tds_box = QFrame()
        tds_box.setStyleSheet("""
            QFrame {
                border: 1px solid #86D0E9;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
        """)
        tds_layout = QHBoxLayout(tds_box)
        tds_layout.addWidget(tds_label)
        tds_layout.addWidget(self.tds_value)
        
        layout.addWidget(ph_box)
        layout.addSpacing(20)
        layout.addWidget(tds_box)

    def startMonitoring(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValues)
        self.timer.start(2000)  # Update every 2 seconds

    def updateValues(self):
        # Simulate pH changes (7.0 - 8.5)
        import random
        new_ph = round(random.uniform(7.0, 8.5), 1)
        self.ph_value.setText(str(new_ph))
        
        # Simulate TDS changes (5-15 ppm)
        new_tds = random.randint(5, 15)
        self.tds_value.setText(f"{new_tds} ppm")

class VideoDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #E6F3F7;
                border: 2px solid #86D0E9;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Video Display For Campaign Water Sustainability")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; color: #2C3E50; font-weight: bold;")
        
        # Placeholder for video content
        video_placeholder = QLabel()
        video_placeholder.setStyleSheet("background-color: #BDE3F0; border-radius: 5px;")
        video_placeholder.setMinimumHeight(200)
        
        layout.addWidget(title)
        layout.addWidget(video_placeholder)

class WaterMonitoringApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Innovative Aqua Solution')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #40E0D0;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Gambar logo Innovative Aqua Solution")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; color: white; font-weight: bold;")
        layout.addWidget(header)
        
        # Video display
        video_display = VideoDisplay()
        layout.addWidget(video_display)
        
        # Monitoring section
        monitoring = MonitoringDisplay()
        layout.addWidget(monitoring)
        
        # Water bottle options
        bottles_container = QWidget()
        bottles_layout = QVBoxLayout(bottles_container)
        
        bottles_title = QLabel("Pilihan Ukuran Air")
        bottles_title.setAlignment(Qt.AlignRight)
        bottles_title.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        bottles_layout.addWidget(bottles_title)
        
        bottles_grid = QGridLayout()
        bottles = [
            ("100 ml", 0, 0), ("350 ml", 0, 1),
            ("600 ml", 1, 0), ("1 Liter", 1, 1)
        ]
        
        for volume, row, col in bottles:
            bottle = WaterBottleWidget(volume)
            bottles_grid.addWidget(bottle, row, col, Qt.AlignCenter)
        
        bottles_layout.addLayout(bottles_grid)
        layout.addWidget(bottles_container)
        
        self.setMinimumSize(800, 700)

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = WaterMonitoringApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()