import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta
import sys
import random
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta

class ModernCard(QFrame):
    clicked = pyqtSignal(str)  # Change signal to emit string
    
    def __init__(self, title, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("ModernCard")
        self.setCursor(Qt.PointingHandCursor)
        self.is_selected = False
        self.title = title  # Store title
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 30, 20, 30)
        
        # Water drop icon
        self.icon_label = QLabel()
        self.updateIcon()
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Title with custom font
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setAlignment(Qt.AlignCenter)
            subtitle_label.setStyleSheet("""
                QLabel {
                    color: #95a5a6;
                    font-size: 14px;
                    margin-top: 5px;
                }
            """)
            layout.addWidget(subtitle_label)
            
        self.updateStyle()
            
    def updateIcon(self):
        icon = qta.icon('fa5s.tint', color='#3498db' if self.is_selected else '#95a5a6')
        self.icon_label.setPixmap(icon.pixmap(32, 32))
        
    def updateStyle(self):
        self.setStyleSheet(f"""
            ModernCard {{
                background: {'white' if self.is_selected else 'rgba(255, 255, 255, 0.95)'};
                border-radius: 20px;
                border: {('2px solid #3498db' if self.is_selected else '1px solid rgba(255, 255, 255, 0.8)')};
            }}
            ModernCard:hover {{
                background: white;
                border: 2px solid {'#3498db' if self.is_selected else '#95a5a6'};
            }}
        """)
        
    def setSelected(self, selected):
        self.is_selected = selected
        self.updateStyle()
        self.updateIcon()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.title)  # Emit title directly

class WaveContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(2000)
        
        # Initialize bubble animation
        self.bubbles = []
        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.updateBubbles)
        
    def startBubbleAnimation(self):
        self.bubble_timer.start(50)
        
    def stopBubbleAnimation(self):
        self.bubble_timer.stop()
        self.bubbles.clear()
        self.update()
        
    def updateBubbles(self):
        # Add new bubbles
        if len(self.bubbles) < 10 and self.value > 0:
            x = self.width() * 0.2 + random.random() * self.width() * 0.6
            self.bubbles.append({
                'x': x,
                'y': self.height(),
                'size': random.randint(4, 8),
                'speed': random.uniform(1, 2)
            })
            
        # Update bubble positions
        for bubble in self.bubbles:
            bubble['y'] -= bubble['speed']
            
        # Remove bubbles that are out of view
        self.bubbles = [b for b in self.bubbles if b['y'] > 0]
        self.update()
        
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
        container = self.rect().adjusted(10, 10, -10, -10)
        
        # Draw wave background
        water_height = int(container.height() * (self.value / 100))
        water_rect = QRect(
            container.left(),
            container.bottom() - water_height,
            container.width(),
            water_height
        )
        
        if self.value > 0:
            # Create wave effect
            wave_path = QPainterPath()
            wave_path.moveTo(water_rect.left(), water_rect.bottom())
            
            wave_width = water_rect.width()
            amplitude = 10.0  # Wave height
            frequency = 2  # Number of waves
            
            for x in range(water_rect.left(), water_rect.right(), 2):
                time_offset = self.value / 50.0
                y = water_rect.top() + amplitude * math.sin((x / wave_width * frequency * math.pi) + time_offset)
                wave_path.lineTo(x, y)
                
            wave_path.lineTo(water_rect.right(), water_rect.bottom())
            wave_path.closeSubpath()
            
            # Create water gradient
            gradient = QLinearGradient(
                water_rect.topLeft(),
                water_rect.bottomLeft()
            )
            gradient.setColorAt(0, QColor(52, 152, 219, 200))
            gradient.setColorAt(1, QColor(41, 128, 185, 200))
            
            painter.fillPath(wave_path, gradient)
            
            # Draw bubbles
            painter.setPen(Qt.NoPen)
            for bubble in self.bubbles:
                bubble_color = QColor(255, 255, 255, 150)
                painter.setBrush(bubble_color)
                painter.drawEllipse(
                    QPointF(bubble['x'], bubble['y']),
                    bubble['size'],
                    bubble['size']
                )

class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Window setup
        self.setWindowTitle('Smart Water Dispenser')
        screen = QDesktopWidget().screenGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.setMinimumSize(1024, 768)
        
        # Modern gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 1, y2: 1,
                    stop: 0 #ECF0F1,
                    stop: 1 #F5F6FA
                );
            }
        """)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(40)
        layout.setContentsMargins(60, 40, 60, 40)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Smart Water Dispenser")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title)
        
        # Right menu items
        menu_widget = QWidget()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setSpacing(20)
        
        menu_items = [
            ("fa5s.moon", "Available: 24/7"),
            ("fa5s.shopping-cart", "Items: 0"),
            ("fa5s.map-marker-alt", "Location")
        ]
        
        for icon_name, text in menu_items:
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setSpacing(8)
            
            icon = qta.icon(icon_name, color='#95a5a6')
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(16, 16))
            item_layout.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("color: #95a5a6; font-size: 14px;")
            item_layout.addWidget(text_label)
            
            menu_layout.addWidget(item)
            
        header_layout.addWidget(menu_widget, alignment=Qt.AlignRight)
        layout.addWidget(header)
        
        # Size selection
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.setSpacing(30)
        
        self.size_cards = []
        sizes = [
            ("Small Size", "Perfect for quick drinks"),
            ("Medium Size", "Most popular choice"),
            ("Large Size", "Family size option")
        ]
        
        for title, subtitle in sizes:
            card = ModernCard(title, subtitle)
            card.clicked.connect(self.selectSize)  # Connect directly to selectSize
            size_layout.addWidget(card)
            self.size_cards.append(card)
            
        layout.addWidget(size_widget)
        
        # Wave container
        self.wave_container = WaveContainer()
        self.wave_container.setFixedHeight(300)
        self.wave_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border-radius: 20px;
                border: 2px solid rgba(52, 152, 219, 0.3);
            }
        """)
        layout.addWidget(self.wave_container)
        
        # Fill button
        self.fill_button = QPushButton("START FILLING")
        self.fill_button.setEnabled(False)
        self.fill_button.setFixedWidth(200)
        self.fill_button.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
        """)
        self.fill_button.clicked.connect(self.startFilling)
        layout.addWidget(self.fill_button, alignment=Qt.AlignCenter)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0,
                    x2: 1, y2: 1,
                    stop: 0 #ECF0F1,
                    stop: 1 #F5F6FA
                );
            }
        """)
        
    def selectSize(self, size):
        self.selected_size = size
        self.fill_button.setEnabled(True)
        
    def startFilling(self):
        self.wave_container.animation.setStartValue(0)
        self.wave_container.animation.setEndValue(100)
        self.wave_container.animation.start()
        self.wave_container.startBubbleAnimation()
        
        self.fill_button.setEnabled(False)
        
        # Reset after animation
        self.wave_container.animation.finished.connect(self.resetFilling)
        
    def resetFilling(self):
        self.fill_button.setEnabled(True)
        self.wave_container.stopBubbleAnimation()
        
        def reset_value():
            self.wave_container.value = 0
            
        QTimer.singleShot(1000, reset_value)

def main():
    # Enable High DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Load custom font
    QFontDatabase.addApplicationFont(":/fonts/Poppins-Regular.ttf")
    QFontDatabase.addApplicationFont(":/fonts/Poppins-Bold.ttf")
    
    app.setFont(QFont("Poppins"))
    
    window = VendingMachine()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()