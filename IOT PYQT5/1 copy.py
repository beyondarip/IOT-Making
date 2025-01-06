import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta
from qt_material import apply_stylesheet
# import resources_rc

class WaterAnimation(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(2000)  # 2 seconds animation
        
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
        container = self.rect()
        painter.setPen(QPen(QColor("#2196F3"), 3))
        painter.setBrush(Qt.transparent)
        painter.drawRoundedRect(container, 15, 15)
        
        # Draw water
        water_height = int(container.height() * (self.value / 100))
        water_rect = QRect(
            container.left() + 3,
            container.bottom() - water_height + 3,
            container.width() - 6,
            water_height - 6
        )
        
        gradient = QLinearGradient(
            water_rect.topLeft(),
            water_rect.bottomLeft()
        )
        gradient.setColorAt(0, QColor("#2196F3"))
        gradient.setColorAt(1, QColor("#64B5F6"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(water_rect, 15, 15)
        
        # Draw bubbles
        if self.value > 0:
            painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
            painter.setBrush(QColor(255, 255, 255, 50))
            
            bubble_positions = [
                (water_rect.center().x() - 20, water_rect.center().y()),
                (water_rect.center().x() + 20, water_rect.center().y() - 15),
                (water_rect.center().x() - 10, water_rect.center().y() + 20)
            ]
            
            for x, y in bubble_positions:
                painter.drawEllipse(QPoint(x, y), 5, 5)

class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('🌊 Smart Water Vending')
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1920, 1080)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add background gradient
        main_widget.setStyleSheet("""
            QWidget {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 1,
                    fx: 0.5, fy: 0.5,
                    stop: 0 #1a237e,
                    stop: 1 #0d47a1
                );
            }
        """)
        
        # Create title
        title_label = QLabel("Smart Water Dispenser")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 36px;
                font-weight: bold;
                margin: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Container for size selection
        size_container = QWidget()
        size_layout = QHBoxLayout(size_container)
        
        # Size selection cards
        self.size_buttons = []
        sizes = [
            ("300ml", "💧", "Small"),
            ("600ml", "💧💧", "Medium"),
            ("1.5L", "💧💧💧", "Large")
        ]
        
        for size, emoji, label in sizes:
            card = QPushButton()
            card.setCheckable(True)
            card.setFixedSize(200, 250)
            card.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 15px;
                    color: white;
                    font-size: 18px;
                    text-align: center;
                }
                QPushButton:checked {
                    background-color: rgba(33, 150, 243, 0.3);
                    border: 2px solid #2196F3;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            
            # Create vertical layout for card content
            card_layout = QVBoxLayout(card)
            
            # Add emoji
            emoji_label = QLabel(emoji)
            emoji_label.setStyleSheet("font-size: 48px; background: transparent;")
            emoji_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(emoji_label)
            
            # Add size text
            size_label = QLabel(size)
            size_label.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent;")
            size_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(size_label)
            
            # Add description
            desc_label = QLabel(label)
            desc_label.setStyleSheet("font-size: 18px; color: rgba(255, 255, 255, 0.7); background: transparent;")
            desc_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(desc_label)
            
            card.clicked.connect(lambda checked, b=card: self.selectSize(b))
            self.size_buttons.append(card)
            size_layout.addWidget(card)
            
        layout.addWidget(size_container)
        
        # Add water animation widget
        self.water_widget = WaterAnimation()
        self.water_widget.setFixedSize(300, 400)
        layout.addWidget(self.water_widget, alignment=Qt.AlignCenter)
        
        # Add fill button
        self.fill_button = QPushButton("Fill Water")
        self.fill_button.setEnabled(False)
        self.fill_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                padding: 15px 50px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: rgba(33, 150, 243, 0.3);
            }
        """)
        self.fill_button.clicked.connect(self.startFilling)
        layout.addWidget(self.fill_button, alignment=Qt.AlignCenter)
        
        # Set dark theme
        apply_stylesheet(self, theme='dark_blue.xml')
        
    def selectSize(self, button):
        # Deselect other buttons
        for btn in self.size_buttons:
            if btn != button:
                btn.setChecked(False)
        
        self.fill_button.setEnabled(button.isChecked())
        
    def startFilling(self):
        self.water_widget.animation.setStartValue(0)
        self.water_widget.animation.setEndValue(100)
        self.water_widget.animation.start()
        
        # Disable buttons during animation
        self.fill_button.setEnabled(False)
        for btn in self.size_buttons:
            btn.setEnabled(False)
            
        # Re-enable buttons after animation
        self.water_widget.animation.finished.connect(self.enableButtons)
        
    def enableButtons(self):
        for btn in self.size_buttons:
            btn.setEnabled(True)
            btn.setChecked(False)
            
def main():
    app = QApplication(sys.argv)
    
    # Enable High DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = VendingMachine()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()