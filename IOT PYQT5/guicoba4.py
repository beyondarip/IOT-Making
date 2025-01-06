import sys
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import random

class WaterButton(QPushButton):
    def __init__(self, icon_path, size_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Wadah ikon dengan ukuran tetap
        icon_container = QWidget()
        icon_container.setFixedSize(120, 120)
        icon_container.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
        """)
        icon_layout = QVBoxLayout(icon_container)
        
        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)
        icon_label.setPixmap(icon_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        # Teks ukuran dengan visibilitas yang lebih baik
        size_label = QLabel(size_text)
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                background-color: transparent;
                padding: 5px;
            }
        """)
        
        layout.addWidget(icon_container)
        layout.addWidget(size_label)
        
        self.setStyleSheet("""
            WaterButton {
                background-color: #F0F8FF;
                border: 2px solid #E1E8ED;
                border-radius: 15px;
                min-height: 180px;
                min-width: 150px;
                margin: 5px;
            }
            WaterButton:hover {
                background-color: #E3F2FD;
                border: 2px solid #BBDEFB;
            }
        """)

class MachineWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Wadah bar progres
        progress_container = QWidget()
        progress_container.setFixedHeight(50)
        progress_container.setStyleSheet("""
            QWidget {
                background-color: #2F3640;
                border-radius: 10px;
                margin: 0px;
            }
        """)
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        
        # Indikator dan progres
        indicator = QLabel("●")
        indicator.setStyleSheet("color: #2ECC71; font-size: 20px;")
        indicator.setFixedWidth(30)
        
        progress = QLabel("▬" * 20)
        progress.setStyleSheet("color: white; font-size: 14px;")
        
        progress_layout.addWidget(indicator)
        progress_layout.addWidget(progress)
        
        # Wadah animasi (bagian hijau)
        animation_container = QWidget()
        animation_container.setFixedHeight(100)
        animation_container.setStyleSheet("""
            QWidget {
                background-color: #2ECC71;
                border-radius: 10px;
                margin: 0px;
            }
        """)
        
        layout.addWidget(progress_container)
        layout.addWidget(animation_container)

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solusi Air Inovatif")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #40E0D0;
            }
        """)
        self.setMinimumSize(1200, 800)
        
        # Widget dan layout utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Layout konten dengan jarak yang lebih baik
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Bagian tampilan video
        self.video_label = QLabel()
        self.video_label.setMinimumSize(720, 405)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border-radius: 20px;
                padding: 5px;
                border: 3px solid #2C3E50;
            }
        """)
        content_layout.addWidget(self.video_label)
        
        # Panel kanan
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(25)
        
        # Bagian ukuran air
        sizes_widget = QWidget()
        sizes_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        sizes_layout = QVBoxLayout(sizes_widget)
        
        # Judul untuk ukuran
        sizes_title = QLabel("Pilihan Ukuran Air")
        sizes_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            padding: 10px;
            margin-bottom: 10px;
        """)
        sizes_layout.addWidget(sizes_title)
        
        # Grid untuk tombol air
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        water_sizes = [
            ("1.png", "100 ml", 0, 0),
            ("2.png", "350 ml", 0, 1),
            ("3.png", "600 ml", 1, 0),
            ("4.png", "1 Liter", 1, 1)
        ]
        
        for icon_path, size, row, col in water_sizes:
            btn = WaterButton(icon_path, size)
            btn.clicked.connect(lambda checked, s=size: self.on_size_selected(s))
            buttons_grid.addWidget(btn, row, col)
        
        sizes_layout.addLayout(buttons_grid)
        
        # Tambah widget mesin
        self.machine_widget = MachineWidget()
        sizes_layout.addWidget(self.machine_widget)
        
        right_layout.addWidget(sizes_widget)
        
        # Bagian pemantauan
        monitoring_widget = QWidget()
        monitoring_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        monitoring_layout = QVBoxLayout(monitoring_widget)
        
        monitoring_title = QLabel("Pemantauan Kualitas Air")
        monitoring_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            padding: 10px;
            margin-bottom: 10px;
        """)
        monitoring_layout.addWidget(monitoring_title)
        
        # Label sensor
        self.ph_label = QLabel("Nilai pH: 8.3")
        self.ph_label.setStyleSheet("""
            background-color: #27AE60;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin: 8px;
        """)
        
        self.tds_label = QLabel("Nilai TDS: 9 ppm")
        self.tds_label.setStyleSheet("""
            background-color: #27AE60;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin: 8px;
        """)
        
        monitoring_layout.addWidget(self.ph_label)
        monitoring_layout.addWidget(self.tds_label)
        
        right_layout.addWidget(monitoring_widget)
        content_layout.addWidget(right_panel)
        
        layout.addLayout(content_layout)
        
        # Setup video dan pembaruan sensor
        self.setup_video()
        self.setup_sensor_updates()
    
    def on_size_selected(self, size):
        print(f"Ukuran yang dipilih: {size}")
    
    def setup_video(self):
        try:
            self.cap = cv2.VideoCapture('yqq.mp4')
            if not self.cap.isOpened():
                raise Exception("Tidak dapat membuka video")
            
            self.video_timer = QTimer()
            self.video_timer.timeout.connect(self.update_frame)
            self.video_timer.start(33)  # 30 FPS
            
        except Exception as e:
            print(f"Error: {str(e)}")
            self.video_label.setText("")
    
    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                if frame is None:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.video_label.setPixmap(scaled_pixmap)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        except Exception as e:
            print(f"Error pembaruan frame: {str(e)}")
    
    def setup_sensor_updates(self):
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensor_values)
        self.sensor_timer.start(2000)
    
    def update_sensor_values(self):
        ph = round(random.uniform(8.0, 8.4), 1)
        self.ph_label.setText(f"Nilai pH: {ph}")
        
        tds = random.randint(6, 10)
        self.tds_label.setText(f"Nilai TDS: {tds} ppm")
    
    def closeEvent(self, event):
        if hasattr(self, 'cap'):
            self.cap.release()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WaterSustainabilityApp()
    window.show()
    sys.exit(app.exec_())