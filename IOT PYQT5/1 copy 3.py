import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta
from qt_material import apply_stylesheet, list_themes
from BlurWindow import blurWindow
from pathlib import Path

class ModernCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, icon, title, subtitle="", parent=None):
        super().__init__(parent)
        self.setObjectName("ModernCard")
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(48, 48))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setAlignment(Qt.AlignCenter)
            subtitle_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
            layout.addWidget(subtitle_label)
            
        self.setStyleSheet("""
            ModernCard {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
            ModernCard:hover {
                background: rgba(255, 255, 255, 1);
                border: 1px solid #3498db;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class WaterContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(2000)
        
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
        
        # Container
        container = self.rect().adjusted(10, 10, -10, -10)
        glass_effect = QLinearGradient(container.topLeft(), container.topRight())
        glass_effect.setColorAt(0, QColor(255, 255, 255, 30))
        glass_effect.setColorAt(1, QColor(255, 255, 255, 10))
        
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        painter.setBrush(glass_effect)
        painter.drawRoundedRect(container, 20, 20)
        
        # Water
        if self.value > 0:
            water_height = int(container.height() * (self.value / 100))
            water_rect = QRect(
                container.left() + 5,
                container.bottom() - water_height + 5,
                container.width() - 10,
                water_height - 10
            )
            
            # Water gradient
            water_gradient = QLinearGradient(
                water_rect.topLeft(),
                water_rect.bottomLeft()
            )
            water_gradient.setColorAt(0, QColor(52, 152, 219, 200))  # Blue
            water_gradient.setColorAt(1, QColor(41, 128, 185, 200))
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(water_gradient)
            
            # Create water wave effect
            path = QPainterPath()
            path.moveTo(water_rect.left(), water_rect.bottom())
            
            wave_height = 10
            wave_count = 3
            wave_width = water_rect.width() / wave_count
            
            for i in range(wave_count + 1):
                x = water_rect.left() + i * wave_width
                y = water_rect.top() + wave_height * (-1 if i % 2 == 0 else 1)
                if i == 0:
                    path.lineTo(x, y)
                else:
                    path.quadTo(
                        x - wave_width/2,
                        water_rect.top() + wave_height * (1 if i % 2 == 0 else -1),
                        x, y
                    )
            
            path.lineTo(water_rect.right(), water_rect.bottom())
            path.closeSubpath()
            
            painter.drawPath(path)
            
            # Add bubbles
            painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
            painter.setBrush(QColor(255, 255, 255, 50))
            
            for i in range(5):
                x = water_rect.left() + (i+1) * water_rect.width()/6
                y = water_rect.top() + (i%3) * water_rect.height()/4
                size = (i%2 + 1) * 5
                painter.drawEllipse(QPointF(x, y), size, size)

class VendingMachine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Window setup
        self.setWindowTitle('Smart Water Vending')
        screen = QDesktopWidget().screenGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.setMinimumSize(1024, 768)
        
        # Set background with blur effect
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(20)
        
        bg = QLabel(self)
        bg.setGeometry(self.rect())
        bg.setStyleSheet("""
            background: qradialgradient(
                cx: 0.5, cy: 0.5, radius: 1,
                fx: 0.5, fy: 0.5,
                stop: 0 #2ecc71,
                stop: 1 #27ae60
            );
        """)
        bg.setGraphicsEffect(blur_effect)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Smart Water Dispenser")
        title.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Stats widget
        stats = QFrame()
        stats.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats)
        
        for icon, text in [
            (qta.icon('fa5s.clock', color='white'), "Average time: 2 min"),
            (qta.icon('fa5s.star', color='white'), "Rating: 4.8/5"),
            (qta.icon('fa5s.check-circle', color='white'), "100% Pure")
        ]:
            stat = QWidget()
            stat_layout = QHBoxLayout(stat)
            
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(24, 24))
            stat_layout.addWidget(icon_label)
            
            text_label = QLabel(text)
            text_label.setStyleSheet("color: white; font-size: 14px;")
            stat_layout.addWidget(text_label)
            
            stats_layout.addWidget(stat)
            
        header_layout.addWidget(stats)
        layout.addWidget(header)
        
        # Size selection
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.setSpacing(20)
        
        self.size_cards = []
        sizes = [
            ("300ml", "Small Size", "Perfect for quick drinks"),
            ("600ml", "Medium Size", "Most popular choice"),
            ("1.5L", "Large Size", "Family size option")
        ]
        
        for size, title, subtitle in sizes:
            card = ModernCard(
                qta.icon('fa5s.tint', color='#3498db'),
                title,
                subtitle
            )
            card.clicked.connect(lambda s=size: self.selectSize(s))
            size_layout.addWidget(card)
            self.size_cards.append(card)
            
        layout.addWidget(size_widget)
        
        # Water container
        self.water_widget = WaterContainer()
        self.water_widget.setMinimumHeight(400)
        layout.addWidget(self.water_widget)
        
        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        self.fill_button = QPushButton("Start Filling")
        self.fill_button.setEnabled(False)
        self.fill_button.setMinimumWidth(200)
        self.fill_button.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 30px;
                font-size: 18px;
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
        
        control_layout.addStretch()
        control_layout.addWidget(self.fill_button)
        control_layout.addStretch()
        
        layout.addWidget(control_panel)
        
        # Set theme
        apply_stylesheet(self, theme='light_blue.xml')
        
    def selectSize(self, size):
        self.selected_size = size
        self.fill_button.setEnabled(True)
        
    def startFilling(self):
        self.water_widget.animation.setStartValue(0)
        self.water_widget.animation.setEndValue(100)
        self.water_widget.animation.start()
        
        self.fill_button.setEnabled(False)
        QTimer.singleShot(2000, lambda: self.fill_button.setEnabled(True))

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = VendingMachine()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()