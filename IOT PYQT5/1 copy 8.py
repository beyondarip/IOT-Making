import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qtawesome as qta
import random
import math

# [ModernCard class implementation remains exactly the same as in your original code]
class ModernCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, title, subtitle="", volume="", parent=None):
        super().__init__(parent)
        self.setObjectName("ModernCard")
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 30, 20, 30)
        
        # Water drop icon with fade-in animation
        icon_label = QLabel()
        icon = qta.icon('fa5s.tint', color='#3498db')
        icon_label.setPixmap(icon.pixmap(32, 32))
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Add fade-in animation
        self.icon_opacity = QGraphicsOpacityEffect(icon_label)
        icon_label.setGraphicsEffect(self.icon_opacity)
        self.icon_animation = QPropertyAnimation(self.icon_opacity, b"opacity")
        self.icon_animation.setDuration(500)
        self.icon_animation.setStartValue(0)
        self.icon_animation.setEndValue(1)
        self.icon_animation.start()
        
        layout.addWidget(icon_label)
        
        # Volume label
        if volume:
            volume_label = QLabel(volume)
            volume_label.setAlignment(Qt.AlignCenter)
            volume_label.setStyleSheet("""
                QLabel {
                    color: #3498db;
                    font-size: 24px;
                    font-weight: bold;
                    margin-top: 5px;
                }
            """)
            layout.addWidget(volume_label)
        
        # Title with custom font
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 10px;
            }
        """)
        layout.addWidget(title_label)
        
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
        
        self.setSelected(False)
        
    def setSelected(self, selected):
        if selected:
            self.setStyleSheet("""
                ModernCard {
                    background: white;
                    border-radius: 20px;
                    border: 2px solid #3498db;
                    box-shadow: 0 4px 6px rgba(52, 152, 219, 0.2);
                }
            """)
        else:
            self.setStyleSheet("""
                ModernCard {
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 20px;
                    border: 1px solid rgba(255, 255, 255, 0.8);
                }
                ModernCard:hover {
                    background: white;
                    border: 2px solid #3498db;
                }
            """)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

# Add new RatingDialog class
class RatingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rate Your Experience")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title with animation
        title = QLabel("How was your experience?")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Add slide-in animation for title
        self.title_anim = QPropertyAnimation(title, b"pos")
        self.title_anim.setDuration(500)
        self.title_anim.setStartValue(QPoint(-400, title.y()))
        self.title_anim.setEndValue(QPoint(title.x(), title.y()))
        self.title_anim.setEasingCurve(QEasingCurve.OutBack)
        self.title_anim.start()
        
        layout.addWidget(title)
        
        # Star rating
        self.star_widget = QWidget()
        star_layout = QHBoxLayout(self.star_widget)
        star_layout.setSpacing(10)
        
        self.stars = []
        for i in range(5):
            star = QPushButton()
            star.setIcon(qta.icon('fa5s.star', color='#bdc3c7'))
            star.setIconSize(QSize(32, 32))
            star.setFixedSize(40, 40)
            star.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    background: rgba(52, 152, 219, 0.1);
                    border-radius: 20px;
                }
            """)
            star.clicked.connect(lambda checked, index=i: self.set_rating(index + 1))
            
            # Add pop-in animation for stars
            self.star_opacity = QGraphicsOpacityEffect(star)
            star.setGraphicsEffect(self.star_opacity)
            self.star_anim = QPropertyAnimation(self.star_opacity, b"opacity")
            self.star_anim.setDuration(200)
            self.star_anim.setStartValue(0)
            self.star_anim.setEndValue(1)
            self.star_anim.setStartTime(i * 100)  # Stagger the animations
            self.star_anim.start()
            
            self.stars.append(star)
            star_layout.addWidget(star)
            
        layout.addWidget(self.star_widget)
        
        # Comment box with animation
        self.comment = QTextEdit()
        self.comment.setPlaceholderText("Add a comment (optional)")
        self.comment.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.comment.setFixedHeight(100)
        
        # Add fade-in animation for comment box
        self.comment_opacity = QGraphicsOpacityEffect(self.comment)
        self.comment.setGraphicsEffect(self.comment_opacity)
        self.comment_anim = QPropertyAnimation(self.comment_opacity, b"opacity")
        self.comment_anim.setDuration(500)
        self.comment_anim.setStartValue(0)
        self.comment_anim.setEndValue(1)
        self.comment_anim.setStartTime(600)  # Start after stars animation
        self.comment_anim.start()
        
        layout.addWidget(self.comment)
        
        # Submit button with animation
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        # Add slide-up animation for submit button
        self.submit_anim = QPropertyAnimation(self.submit_btn, b"pos")
        self.submit_anim.setDuration(500)
        self.submit_anim.setStartValue(QPoint(self.submit_btn.x(), 400))
        self.submit_anim.setEndValue(QPoint(self.submit_btn.x(), self.submit_btn.y()))
        self.submit_anim.setEasingCurve(QEasingCurve.OutBack)
        self.submit_anim.setStartTime(800)  # Start after comment box animation
        self.submit_anim.start()
        
        self.submit_btn.clicked.connect(self.accept)
        layout.addWidget(self.submit_btn)
        
        self.rating = 0
        
    def set_rating(self, rating):
        self.rating = rating
        for i, star in enumerate(self.stars):
            if i < rating:
                star.setIcon(qta.icon('fa5s.star', color='#f1c40f'))
                # Add pop animation for selected stars
                anim = QPropertyAnimation(star, b"geometry")
                anim.setDuration(200)
                current_geo = star.geometry()
                anim.setKeyValueAt(0.5, QRect(current_geo.x(), current_geo.y() - 10,
                                            current_geo.width(), current_geo.height()))
                anim.setEndValue(current_geo)
                anim.start()
            else:
                star.setIcon(qta.icon('fa5s.star', color='#bdc3c7'))

# Complete WaveContainer class with all methods
class WaveContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.setDuration(2000)
        
        # Percentage label
        self.percentage_label = QLabel("0%", self)
        self.percentage_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                padding: 5px 15px;
            }
        """)
        self.percentage_label.hide()
        
        # Initialize bubble animation
        self.bubbles = []
        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.updateBubbles)
        
    def resizeEvent(self, event):
        # Center the percentage label
        self.percentage_label.move(
            (self.width() - self.percentage_label.width()) // 2,
            (self.height() - self.percentage_label.height()) // 2
        )
        super().resizeEvent(event)
        
    def startBubbleAnimation(self):
        self.bubble_timer.start(50)
        self.percentage_label.show()
        
    def stopBubbleAnimation(self):
        self.bubble_timer.stop()
        self.bubbles.clear()
        self.percentage_label.hide()
        self.update()
        
    def updateBubbles(self):
        # Update percentage label
        self.percentage_label.setText(f"{int(self.value)}%")
        self.percentage_label.adjustSize()
        self.percentage_label.move(
            (self.width() - self.percentage_label.width()) // 2,
            (self.height() - self.percentage_label.height()) // 2
        )
        
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
            amplitude = 10.0
            frequency = 2
            
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
        self.selected_size = None
        self.size_cards = []
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
        
        # Title with water icon
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setSpacing(15)
        
        water_icon = QLabel()
        icon = qta.icon('fa5s.tint', color='#3498db')
        water_icon.setPixmap(icon.pixmap(40, 40))
        title_layout.addWidget(water_icon)
        
        title = QLabel("Smart Water Dispenser")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        title_layout.addWidget(title)
        
        header_layout.addWidget(title_widget)
        
        # Right menu items
        menu_widget = QWidget()
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setSpacing(20)
        
        menu_items = [
            ("fa5s.clock", "24/7 Service"),
            ("fa5s.temperature-low", "Cool & Fresh"),
            ("fa5s.shield-alt", "Hygienic")
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
        
        sizes = [
            ("Small", "Perfect for quick drinks", "300ml"),
            ("Medium", "Most popular choice", "600ml"),
            ("Large", "Family size option", "1.5L")
        ]
        
        for title, subtitle, volume in sizes:
            card = ModernCard(title, subtitle, volume)
            card.clicked.connect(lambda checked=False, t=title, c=card: self.selectSize(t, c))
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
        
    def selectSize(self, size, card):
        self.selected_size = size
        self.fill_button.setEnabled(True)
        
        # Update card selections
        for c in self.size_cards:
            c.setSelected(c == card)
            
            # Add scale animation for selected card
            scale_anim = QPropertyAnimation(c, b"geometry")
            scale_anim.setDuration(200)
            current_geo = c.geometry()
            
            if c == card:
                # Scale up selected card
                scale_anim.setEndValue(QRect(
                    current_geo.x() - 5,
                    current_geo.y() - 5,
                    current_geo.width() + 10,
                    current_geo.height() + 10
                ))
            else:
                # Reset other cards
                scale_anim.setEndValue(current_geo)
                
            scale_anim.start()
        
    def startFilling(self):
        self.fill_button.setEnabled(False)
        
        # Disable size selection during filling
        for card in self.size_cards:
            card.setEnabled(False)
        
        self.wave_container.animation.setStartValue(0)
        self.wave_container.animation.setEndValue(100)
        self.wave_container.animation.start()
        self.wave_container.startBubbleAnimation()
        
        # Reset after animation
        self.wave_container.animation.finished.connect(self.resetFilling)
        
    def resetFilling(self):
        try:
            # Hentikan animasi gelombang terlebih dahulu
            self.wave_container.stopBubbleAnimation()
        # Show rating dialog
        rating_dialog = RatingDialog(self)
        if rating_dialog.exec_() == QDialog.Accepted:
            rating = rating_dialog.rating
            comment = rating_dialog.comment.toPlainText()
            
            # Here you could save the rating and comment to a file or database
            print(f"Rating: {rating}/5")
            print(f"Comment: {comment}")
        
        # Re-enable size selection with animation
        for card in self.size_cards:
            card.setEnabled(True)
            card.setSelected(False)
            
            # Add bounce animation
            bounce_anim = QPropertyAnimation(card, b"geometry")
            bounce_anim.setDuration(500)
            bounce_anim.setEasingCurve(QEasingCurve.OutBounce)
            
            current_geo = card.geometry()
            bounce_anim.setStartValue(QRect(
                current_geo.x(), 
                current_geo.y() + 20, 
                current_geo.width(), 
                current_geo.height()
            ))
            bounce_anim.setEndValue(current_geo)
            bounce_anim.start()
        
        self.selected_size = None
        self.wave_container.stopBubbleAnimation()
        
        def reset_value():
            self.wave_container.value = 0
            self.wave_container.update()
            except Exception as e:
            print(f"Error dalam reset_value: {str(e)}")
            
        QTimer.singleShot(1000, reset_value)

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    QFontDatabase.addApplicationFont(":/fonts/Poppins-Regular.ttf")
    QFontDatabase.addApplicationFont(":/fonts/Poppins-Bold.ttf")
    
    app.setFont(QFont("Poppins"))
    
    window = VendingMachine()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()