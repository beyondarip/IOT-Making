import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Modern color palette
COLORS = {
    'primary': '#2563EB',    # Blue
    'secondary': '#10B981',  # Green
    'accent': '#8B5CF6',    # Purple
    'background': '#F8FAFC', 
    'surface': '#FFFFFF',
    'text': '#1E293B',
    'light_text': '#64748B'
}

class WaterVendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Smart Water Vending Machine')
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QGroupBox {{
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
                margin-top: 1em;
                font-size: 14px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                color: {COLORS['primary']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QRadioButton {{
                color: {COLORS['text']};
                font-size: 13px;
                padding: 5px;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left section (Video + Water Quality)
        left_section = QVBoxLayout()
        
        # Video player
        video_container = QGroupBox("Advertisement Display")
        video_layout = QVBoxLayout(video_container)
        web_view = QWebEngineView()
        web_view.setUrl(QUrl("https://www.youtube.com/embed/gsT6eKsnT0M"))
        web_view.setMinimumSize(600, 400)
        video_layout.addWidget(web_view)
        left_section.addWidget(video_container, stretch=3)

        # Water quality metrics (bottom left)
        metrics_container = QGroupBox("Water Quality Metrics")
        metrics_container.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                padding: 10px;
            }}
            .value-label {{
                color: {COLORS['primary']};
                font-weight: bold;
                font-size: 20px;
            }}
        """)
        
        metrics_layout = QVBoxLayout(metrics_container)
        
        # pH Value with custom styling
        ph_widget = QWidget()
        ph_layout = QHBoxLayout(ph_widget)
        ph_icon = QLabel("💧")
        ph_icon.setFont(QFont("Segoe UI Emoji", 20))
        ph_label = QLabel("pH Level:")
        self.ph_value = QLabel("7.0")
        self.ph_value.setProperty("class", "value-label")
        ph_layout.addWidget(ph_icon)
        ph_layout.addWidget(ph_label)
        ph_layout.addWidget(self.ph_value)
        ph_layout.addStretch()
        
        # TDS Value
        tds_widget = QWidget()
        tds_layout = QHBoxLayout(tds_widget)
        tds_icon = QLabel("🔍")
        tds_icon.setFont(QFont("Segoe UI Emoji", 20))
        tds_label = QLabel("TDS Level:")
        self.tds_value = QLabel("150 ppm")
        self.tds_value.setProperty("class", "value-label")
        tds_layout.addWidget(tds_icon)
        tds_layout.addWidget(tds_label)
        tds_layout.addWidget(self.tds_value)
        tds_layout.addStretch()
        
        metrics_layout.addWidget(ph_widget)
        metrics_layout.addWidget(tds_widget)
        left_section.addWidget(metrics_container, stretch=1)
        
        # Right section (Bottle selection + Filling)
        right_section = QVBoxLayout()
        
        # Bottle selection (2x2 grid)
        bottles_container = QGroupBox("Select Bottle Size")
        bottles_layout = QGridLayout(bottles_container)
        
        self.bottle_group = QButtonGroup()
        
        bottle_sizes = [
            ("100ml", ":/images/bottle_100.png", "🥤"),
            ("350ml", ":/images/bottle_350.png", "🥤"),
            ("600ml", ":/images/bottle_600.png", "🥤"),
            ("1 Liter", ":/images/bottle_1000.png", "🥤")
        ]
        
        for i, (size, image_path, fallback) in enumerate(bottle_sizes):
            bottle_widget = QWidget()
            bottle_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS['surface']};
                    border-radius: 10px;
                    padding: 10px;
                }}
                QWidget:hover {{
                    background-color: {COLORS['background']};
                }}
            """)
            
            bottle_layout = QVBoxLayout(bottle_widget)
            
            try:
                image_label = QLabel()
                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    raise FileNotFoundError
                image_label.setPixmap(pixmap.scaled(120, 240, Qt.KeepAspectRatio))
            except:
                image_label = QLabel(fallback)
                image_label.setFont(QFont("Segoe UI Emoji", 50))
            
            radio_button = QRadioButton(size)
            self.bottle_group.addButton(radio_button, i)
            
            bottle_layout.addWidget(image_label, alignment=Qt.AlignCenter)
            bottle_layout.addWidget(radio_button, alignment=Qt.AlignCenter)
            bottles_layout.addWidget(bottle_widget, i//2, i%2)
        
        right_section.addWidget(bottles_container)
        
        # Filling section
        filling_container = QGroupBox("Filling Status")
        filling_layout = QVBoxLayout(filling_container)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['primary']};
                border-radius: 8px;
                text-align: center;
                height: 25px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['secondary']};
                border-radius: 6px;
            }}
        """)
        
        self.start_button = QPushButton("Start Filling")
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['light_text']};
            }}
        """)
        
        filling_layout.addWidget(self.progress_bar)
        filling_layout.addWidget(self.start_button)
        
        right_section.addWidget(filling_container)
        
        # Add sections to main layout
        main_layout.addLayout(left_section, stretch=2)
        main_layout.addLayout(right_section, stretch=1)
        
        # Connect signals
        self.start_button.clicked.connect(self.start_filling)
        self.bottle_group.buttonClicked.connect(self.bottle_selected)
        
        # Initialize state
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Setup timer for simulated real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)
        
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