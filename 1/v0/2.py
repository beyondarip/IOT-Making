import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WaterVendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Smart Water Vending Machine')
        self.setMinimumSize(1200, 800)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top section with video and water quality metrics
        top_section = QHBoxLayout()
        
        # Video player (YouTube)
        video_container = QGroupBox("Advertisement")
        video_layout = QVBoxLayout(video_container)
        web_view = QWebEngineView()
        web_view.setUrl(QUrl("https://www.youtube.com/embed/gsT6eKsnT0M"))
        web_view.setMinimumSize(400, 300)
        video_layout.addWidget(web_view)
        
        # Water quality metrics
        metrics_container = QGroupBox("Water Quality")
        metrics_layout = QVBoxLayout(metrics_container)
        
        # pH Value
        ph_layout = QHBoxLayout()
        ph_label = QLabel("pH Value:")
        self.ph_value = QLabel("7.0")
        ph_layout.addWidget(ph_label)
        ph_layout.addWidget(self.ph_value)
        
        # TDS Value
        tds_layout = QHBoxLayout()
        tds_label = QLabel("TDS Value:")
        self.tds_value = QLabel("150 ppm")
        tds_layout.addWidget(tds_label)
        tds_layout.addWidget(self.tds_value)
        
        metrics_layout.addLayout(ph_layout)
        metrics_layout.addLayout(tds_layout)
        
        top_section.addWidget(video_container, stretch=2)
        top_section.addWidget(metrics_container, stretch=1)
        layout.addLayout(top_section)
        
        # Bottle selection section
        bottles_container = QGroupBox("Select Bottle Size")
        bottles_layout = QHBoxLayout(bottles_container)
        
        self.bottle_group = QButtonGroup()
        
        bottle_sizes = [
            ("100ml", ":/images/bottle_100.png", "🥤"),
            ("350ml", ":/images/bottle_350.png", "🥤"),
            ("600ml", ":/images/bottle_600.png", "🥤"),
            ("1 Liter", ":/images/bottle_1000.png", "🥤")
        ]
        
        for i, (size, image_path, fallback) in enumerate(bottle_sizes):
            bottle_widget = QWidget()
            bottle_layout = QVBoxLayout(bottle_widget)
            
            # Try to load image, use fallback if failed
            try:
                image_label = QLabel()
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    raise FileNotFoundError
                image_label.setPixmap(pixmap.scaled(100, 200, Qt.KeepAspectRatio))
            except:
                image_label = QLabel(fallback)
                image_label.setFont(QFont("Segoe UI Emoji", 40))
            
            radio_button = QRadioButton(size)
            self.bottle_group.addButton(radio_button, i)
            
            bottle_layout.addWidget(image_label, alignment=Qt.AlignCenter)
            bottle_layout.addWidget(radio_button, alignment=Qt.AlignCenter)
            bottles_layout.addWidget(bottle_widget)
        
        layout.addWidget(bottles_container)
        
        # Start filling button and progress
        control_container = QGroupBox()
        control_layout = QVBoxLayout(control_container)
        
        self.start_button = QPushButton("Start Filling")
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.progress_bar)
        
        layout.addWidget(control_container)
        
        # Connect signals
        self.start_button.clicked.connect(self.start_filling)
        self.bottle_group.buttonClicked.connect(self.bottle_selected)
        
        # Initialize state
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Setup timer for simulated real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # Update every second
        
    def bottle_selected(self):
        self.start_button.setEnabled(True)
        
    def start_filling(self):
        self.start_button.setEnabled(False)
        
        # Simulate filling process
        self.progress = 0
        self.fill_timer = QTimer()
        self.fill_timer.timeout.connect(self.update_progress)
        self.fill_timer.start(100)
        
    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        
        if self.progress >= 100:
            self.fill_timer.stop()
            self.start_button.setEnabled(True)
            self.bottle_group.setExclusive(False)
            for button in self.bottle_group.buttons():
                button.setChecked(False)
            self.bottle_group.setExclusive(True)
            
    def update_metrics(self):
        # Simulate real-time pH and TDS updates
        import random
        self.ph_value.setText(f"{random.uniform(6.8, 7.2):.1f}")
        self.tds_value.setText(f"{random.randint(145, 155)} ppm")

def main():
    app = QApplication(sys.argv)
    window = WaterVendingMachine()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()