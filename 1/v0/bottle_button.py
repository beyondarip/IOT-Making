from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class BottleButton(QPushButton):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.setCheckable(True)
        self.setFixedSize(120, 120)  # Slightly smaller
        
        # Try to load bottle image, use emoji as fallback
        try:
            self.setIcon(QIcon(f"images/bottle_{size}.png"))
            self.setIconSize(QSize(60, 60))
        except:
            self.setText(f"🍶\n{size}")
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                color: #495057;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #e7f5ff;
                border: 3px solid #339af0;
                color: #1971c2;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #339af0;
            }
        """)