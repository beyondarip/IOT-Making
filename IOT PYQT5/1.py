import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# import resources_rc  # Import resources file

class WaterAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    @pyqtProperty(float)
    def value(self):
        return self._value
        
    @value.setter
    def value(self, value):
        self._value = value
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw container
        container = QRect(0, 0, self.width(), self.height())
        painter.setPen(QPen(QColor("#2196F3"), 3))
        painter.setBrush(Qt.transparent)
        painter.drawRoundedRect(container, 10, 10)
        
        # Draw water
        water_height = int(self.height() * (self._value / 100))
        water = QRect(0, self.height() - water_height, self.width(), water_height)
        gradient = QLinearGradient(water.topLeft(), water.bottomLeft())
        gradient.setColorAt(0, QColor("#2196F3"))
        gradient.setColorAt(1, QColor("#64B5F6"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(water, 10, 10)
        
        # Draw water percentage
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(container, Qt.AlignCenter, f"{int(self._value)}%")

class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('Water Vending Machine 🌊')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLabel {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Add title
        title = QLabel("Select Water Volume 💧")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Create volume selection buttons
        self.volume_group = QButtonGroup(self)
        volumes = [
            ("300ml", "🥤"),
            ("600ml", "🍶"),
            ("1.5L", "🫙")
        ]
        
        volume_layout = QHBoxLayout()
        for i, (text, emoji) in enumerate(volumes):
            btn = QPushButton(f"{emoji}\n{text}")
            btn.setFixedSize(120, 120)
            btn.setCheckable(True)
            self.volume_group.addButton(btn, i)
            volume_layout.addWidget(btn)
            
        layout.addLayout(volume_layout)
        
        # Add water animation widget
        self.water_animation = WaterAnimation()
        self.water_animation.setFixedSize(200, 300)
        layout.addWidget(self.water_animation, alignment=Qt.AlignCenter)
        
        # Add fill button
        self.fill_button = QPushButton("Fill Water 🚰")
        self.fill_button.setEnabled(False)
        self.fill_button.setFixedSize(200, 50)
        layout.addWidget(self.fill_button, alignment=Qt.AlignCenter)
        
        # Connect signals
        self.volume_group.buttonClicked.connect(self.enableFillButton)
        self.fill_button.clicked.connect(self.startFilling)
        
        # Set window size and center it
        self.setFixedSize(500, 700)
        self.center()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def enableFillButton(self):
        self.fill_button.setEnabled(True)
        self.water_animation.value = 0
        
    def startFilling(self):
        self.fill_button.setEnabled(False)
        for btn in self.volume_group.buttons():
            btn.setEnabled(False)
            
        self.water_animation.animation.setDuration(3000)  # 3 seconds
        self.water_animation.animation.setStartValue(0)
        self.water_animation.animation.setEndValue(100)
        
        # Add animation finished handler
        self.water_animation.animation.finished.connect(self.resetUI)
        self.water_animation.animation.start()
        
    def resetUI(self):
        # Re-enable all buttons after 2 seconds
        QTimer.singleShot(2000, lambda: [
            btn.setEnabled(True) for btn in self.volume_group.buttons()
        ])
        self.volume_group.setExclusive(False)
        for btn in self.volume_group.buttons():
            btn.setChecked(False)
        self.volume_group.setExclusive(True)

def main():
    app = QApplication(sys.argv)
    # Set application-wide font
    font_db = QFontDatabase()
    font_id = font_db.addApplicationFont(":/fonts/Poppins-Regular.ttf")
    if font_id != -1:
        font_families = font_db.applicationFontFamilies(font_id)
        if font_families:
            app.setFont(QFont(font_families[0], 10))
    
    window = VendingMachine()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()