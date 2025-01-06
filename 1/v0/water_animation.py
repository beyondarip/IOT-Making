from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WaterFillingAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.percentage = 0
        self.animation = QPropertyAnimation(self, b"percentage")
        self.animation.setDuration(3000)  # 3 seconds
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        
        self.setFixedSize(150, 250)  # Fixed size for better control
        
    @pyqtProperty(float)
    def percentage(self):
        return self._percentage
        
    @percentage.setter
    def percentage(self, value):
        self._percentage = value
        self.update()
        
    def start_animation(self):
        self.animation.start()
        
    def reset(self):
        self.animation.stop()
        self.percentage = 0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center the bottle in the widget
        rect_width = 80
        rect_height = 180
        x = (self.width() - rect_width) // 2
        y = (self.height() - rect_height) // 2
        
        # Draw bottle outline
        bottle_path = QPainterPath()
        bottle_path.addRoundedRect(QRectF(x, y, rect_width, rect_height), 8, 8)
        
        # Draw water level
        water_height = (rect_height * self.percentage) / 100
        water_rect = QRectF(x, y + rect_height - water_height, rect_width, water_height)
        
        # Create gradient for water
        gradient = QLinearGradient(water_rect.topLeft(), water_rect.bottomLeft())
        gradient.setColorAt(0, QColor(33, 147, 176))
        gradient.setColorAt(1, QColor(109, 213, 237))
        
        painter.setPen(QPen(QColor("#495057"), 2))
        painter.drawPath(bottle_path)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawRect(water_rect)
        
        # Draw percentage text
        painter.setPen(QColor("#495057"))
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{int(self.percentage)}%")