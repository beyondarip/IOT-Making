import sys
import cv2
import time
import logging
import threading
import os
import requests
import json
from typing import Optional, Dict
from dataclasses import dataclass
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                           QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
                           QFrame, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal, QMutex, QMutexLocker,QObject
from PyQt5.QtGui import QImage, QPixmap, QFont, QPalette, QColor


from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                           QProgressBar, QWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
import uuid

# Setup logging with proper configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vending_machine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Hardware Configuration
try:
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    logger.warning("RPi.GPIO not available - running in simulation mode")
    HARDWARE_AVAILABLE = False


# Water volume configurations
@dataclass
class WaterVolume:
    name: str
    pulses: int
    display_name: str
    price: str

WATER_VOLUMES = {
    "100 ml": WaterVolume("100 ml", 108, "100 ml", "Rp. 3.000"),
    "350 ml": WaterVolume("350 ml", 378, "350 ml", "Rp. 5.000"),
    "600 ml": WaterVolume("600 ml", 670, "600 ml", "Rp. 7.000"),
    "600 ml": WaterVolume("600 ml", 670, "600 ml", "Rp. 7.000"),
    "1 Liter": WaterVolume("1 Liter", 1080, "1 Liter", "Rp. 15.000")
}

import json
from dataclasses import dataclass
import time, requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    base_url: str
    machine_id: str
    timeout: int
    retry_attempts: int
    retry_delay: int

@dataclass
class HardwareConfig:
    flow_sensor_pin: int
    motor_pin: int
    esp32_ip: str
    esp32_port: int

@dataclass
class AppConfig:
    video_path: str
    log_file: str
    log_level: str
    update_interval: int



class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_path = 'config.json'
            self.api_config: Optional[APIConfig] = None
            self.hardware_config: Optional[HardwareConfig] = None
            self.app_config: Optional[AppConfig] = None
            self.load_config()
            self.initialized = True
    
    def load_config(self):
        """Load configuration from JSON file with fallback values"""
        try:
            if not os.path.exists(self.config_path):
                self._create_default_config()
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.api_config = APIConfig(
                base_url=config['api']['base_url'],
                machine_id=config['api']['machine_id'],
                timeout=config['api']['timeout'],
                retry_attempts=config['api']['retry_attempts'],
                retry_delay=config['api']['retry_delay']
            )
            
            self.hardware_config = HardwareConfig(
                flow_sensor_pin=config['hardware']['flow_sensor_pin'],
                motor_pin=config['hardware']['motor_pin'],
                esp32_ip=config['hardware']['esp32_ip'],
                esp32_port=config['hardware']['esp32_port']
            )
            
            self.app_config = AppConfig(
                video_path=config['app']['video_path'],
                log_file=config['app']['log_file'],
                log_level=config['app']['log_level'],
                update_interval=config['app']['update_interval']
            )
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'api': {
                'base_url': 'http://localhost:8000',
                'machine_id': 'VM001',
                'timeout': 5,
                'retry_attempts': 3,
                'retry_delay': 1
            },
            'hardware': {
                'flow_sensor_pin': 20,
                'motor_pin': 21,
                'esp32_ip': '192.168.137.82',
                'esp32_port': 80
            },
            'app': {
                'video_path': 'yqq.mkv',
                'log_file': 'vending_machine.log',
                'log_level': 'INFO',
                'update_interval': 2
            }
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info("Created default configuration file")
            self.load_config()
        except Exception as e:
            logger.error(f"Error creating default config: {e}")
            raise

    def save_config(self):
        """Save current configuration to file"""
        config = {
            'api': {
                'base_url': self.api_config.base_url,
                'machine_id': self.api_config.machine_id,
                'timeout': self.api_config.timeout,
                'retry_attempts': self.api_config.retry_attempts,
                'retry_delay': self.api_config.retry_delay
            },
            'hardware': {
                'flow_sensor_pin': self.hardware_config.flow_sensor_pin,
                'motor_pin': self.hardware_config.motor_pin,
                'esp32_ip': self.hardware_config.esp32_ip,
                'esp32_port': self.hardware_config.esp32_port
            },
            'app': {
                'video_path': self.app_config.video_path,
                'log_file': self.app_config.log_file,
                'log_level': self.app_config.log_level,
                'update_interval': self.app_config.update_interval
            }
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise


class APIClient:
    """Handle all API communications with backend"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Configure requests session"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request with retry mechanism and proper error handling
        """
        url = f"{self.config.api_config.base_url}/api/{endpoint}"
        retries = self.config.api_config.retry_attempts
        
        for attempt in range(retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    timeout=self.config.api_config.timeout
                )
                
                response.raise_for_status()
                return response.json()
                
            except RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                
                if attempt < retries - 1:
                    time.sleep(self.config.api_config.retry_delay)
                    continue
                    
                logger.error(f"Request failed after {retries} attempts: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error in API request: {e}")
                return None
    
    def record_quality(self, quality_data: Dict[str, float]) -> bool:
        """
        Record water quality data
        
        Args:
            quality_data: Dictionary containing tds_level, ph_level, and water_level
        
        Returns:
            bool: True if successful, False otherwise
        """
        endpoint = f"machines/{self.config.api_config.machine_id}/record_quality/"
        
        try:
            result = self._make_request('POST', endpoint, quality_data)
            return result is not None
        except Exception as e:
            logger.error(f"Error recording quality data: {e}")
            return False
    
    def record_sale(self, sale_data: Dict[str, Any]) -> bool:
        """
        Record sales data
        
        Args:
            sale_data: Dictionary containing volume and price
        
        Returns:
            bool: True if successful, False otherwise
        """
        endpoint = f"machines/{self.config.api_config.machine_id}/record_sale/"
        
        try:
            result = self._make_request('POST', endpoint, sale_data)
            return result is not None
        except Exception as e:
            logger.error(f"Error recording sale data: {e}")
            return False

import midtransclient
import json
import logging
from dataclasses import dataclass
from typing import Optional, Dict

logger = logging.getLogger(__name__)

@dataclass
class PaymentConfig:
    server_key: str
    client_key: str
    merchant_id: str
    is_production: bool = False

class MidtransPayment:
    def __init__(self, config: PaymentConfig):
        self.config = config
        self.snap = midtransclient.Snap(
            is_production=config.is_production,
            server_key=config.server_key,
            client_key=config.client_key
        )

    def create_transaction(self, order_id: str, amount: int, item_name: str) -> Optional[Dict]:
        """
        Create a Midtrans payment transaction
        
        Args:
            order_id: Unique order ID
            amount: Amount in IDR
            item_name: Name of the water volume being purchased
            
        Returns:
            Dictionary containing transaction token and redirect URL
        """
        try:
            transaction_details = {
                "order_id": order_id,
                "gross_amount": amount
            }

            item_details = [{
                "id": "WATER1",
                "price": amount,
                "quantity": 1,
                "name": item_name
            }]

            transaction = {
                "transaction_details": transaction_details,
                "item_details": item_details
            }

            transaction_token = self.snap.create_transaction(transaction)
            
            return {
                "token": transaction_token["token"],
                "redirect_url": transaction_token["redirect_url"]
            }

        except Exception as e:
            logger.error(f"Error creating Midtrans transaction: {e}")
            return None

    def check_transaction_status(self, order_id: str) -> Optional[str]:
        """
        Check the status of a transaction
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Transaction status or None if error
        """
        try:
            status_response = self.snap.transactions.status(order_id)
            return status_response["transaction_status"]
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return None

class PaymentManager:
    def __init__(self):
        self.config = self._load_payment_config()
        self.payment_client = MidtransPayment(self.config)
        
    def _load_payment_config(self) -> PaymentConfig:
        """Load Midtrans configuration from config file"""
        try:
            with open('payment_config.json', 'r') as f:
                config = json.load(f)
                return PaymentConfig(
                    server_key=config['server_key'],
                    client_key=config['client_key'],
                    merchant_id=config['merchant_id'],
                    is_production=config.get('is_production', False)
                )
        except Exception as e:
            logger.error(f"Error loading payment config: {e}")
            raise

class PaymentDialog(QDialog):
    payment_completed = pyqtSignal(bool)  # True if successful, False if failed/cancelled
    
    def __init__(self, payment_manager, amount: int, item_name: str, parent=None):
        super().__init__(parent)
        self.payment_manager = payment_manager
        self.amount = amount
        self.item_name = item_name
        self.order_id = f"ORDER-{uuid.uuid4().hex[:8]}"
        self.status_check_timer = QTimer()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Payment")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create WebView for Midtrans Snap
        self.web_view = QWebEngineView()
        self.web_view.setFixedSize(780, 550)
        
        # Create and start payment
        transaction = self.payment_manager.payment_client.create_transaction(
            self.order_id,
            self.amount,
            self.item_name
        )
        
        if transaction:
            from PyQt5.QtCore import QUrl
            # self.web_view.load(transaction["redirect_url"])
            self.web_view.load(QUrl(transaction["redirect_url"]))
            
            # Setup status checking
            self.status_check_timer.timeout.connect(self.check_payment_status)
            self.status_check_timer.start(5000)  # Check every 5 seconds
        else:
            self.payment_completed.emit(False)
            self.close()
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        
    def check_payment_status(self):
        """Check payment status periodically"""
        status = self.payment_manager.payment_client.check_transaction_status(self.order_id)
        
        if status == "settlement":
            self.status_check_timer.stop()
            self.payment_completed.emit(True)
            self.close()
        elif status in ["deny", "cancel", "expire"]:
            self.status_check_timer.stop()
            self.payment_completed.emit(False)
            self.close()
            
    def closeEvent(self, event):
        """Handle dialog close"""
        self.status_check_timer.stop()
        event.accept()

class HardwareController:
    """Manages hardware interactions with proper error handling and simulation support."""
    

    def __init__(self):
        self.config = ConfigManager()
        self.is_simulated = not HARDWARE_AVAILABLE
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Initialize GPIO with proper error handling."""
        if self.is_simulated:
            return
            
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.config.hardware_config.flow_sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.config.hardware_config.motor_pin, GPIO.OUT)
            GPIO.output(self.config.hardware_config.motor_pin, GPIO.LOW)
            logger.info("GPIO setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            self.is_simulated = True
    
    def start_motor(self):
        """Start the water pump motor."""
        if self.is_simulated:
            logger.info("Simulated motor start")
            return True
            
        try:
            GPIO.output(MOTOR_PIN, GPIO.HIGH)
            logger.info("Motor started")
            return True
        except Exception as e:
            logger.error(f"Failed to start motor: {e}")
            return False
    
    def stop_motor(self):
        """Stop the water pump motor."""
        if self.is_simulated:
            logger.info("Simulated motor stop")
            return
            
        try:
            GPIO.output(MOTOR_PIN, GPIO.LOW)
            logger.info("Motor stopped")
        except Exception as e:
            logger.error(f"Failed to stop motor: {e}")
    
    def cleanup(self):
        """Clean up GPIO resources."""
        if self.is_simulated:
            return
            
        try:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"GPIO cleanup failed: {e}")

class WaterController(QObject):
    """Controls water dispensing with flow sensor monitoring."""
    
    update_progress = pyqtSignal(int)
    filling_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.hardware = HardwareController()
        self.api_client = APIClient()
        self.pulse_count = 0
        self.is_running = False
        self.target_pulses = 0
        self._lock = threading.Lock()
        
    def pulse_callback(self, channel):
        """Handle flow sensor pulse with thread safety."""
        if not self.is_running:
            return
            
        with self._lock:
            self.pulse_count += 1
            progress = min(100, int((self.pulse_count / self.target_pulses) * 100))
            self.update_progress.emit(progress)
            
            if self.pulse_count >= self.target_pulses:
                self.stop_filling()
    
    def start_filling(self, size: str) -> bool:
        """Start the water filling process for given size."""
        if size not in WATER_VOLUMES:
            self.error_occurred.emit("Invalid size selected")
            return False

        volume = WATER_VOLUMES[size]
        self.target_pulses = volume.pulses
        self.pulse_count = 0
        self.is_running = True
        
        logger.info(f"Starting filling process for {size} with target {self.target_pulses} pulses")
        
        # Start filling process in separate thread
        threading.Thread(target=self._filling_process, daemon=True).start()
        return True
    
    def _filling_process(self):
        """Handle the filling process with proper error handling."""
        try:
            if not self.hardware.start_motor():
                self.error_occurred.emit("Failed to start motor")
                return
                
            if not self.hardware.is_simulated:
                GPIO.add_event_detect(self.config.hardware_config.flow_sensor_pin, GPIO.FALLING, 
                                    callback=self.pulse_callback)
            else:
                # Simulate flow sensor pulses in simulation mode
                self._simulate_flow()
                
        except Exception as e:
            logger.error(f"Error in filling process: {e}")
            self.error_occurred.emit(f"Filling error: {str(e)}")
            self.stop_filling()
    
    def _simulate_flow(self):
        """Simulate flow sensor pulses when hardware is not available."""
        while self.is_running and self.pulse_count < self.target_pulses:
            time.sleep(0.1)  # Simulate 10 pulses per second
            self.pulse_callback(None)
    
    def stop_filling(self):
        """Stop the filling process safely and record sale."""
        self.is_running = False
        self.hardware.stop_motor()
        
        if not self.hardware.is_simulated:
            try:
                GPIO.remove_event_detect(self.config.hardware_config.flow_sensor_pin)
            except Exception as e:
                logger.warning(f"Failed to remove event detection: {e}")
        
        # Record sale if completed successfully
        if hasattr(self, 'current_volume'):
            try:
                sale_data = {
                    'volume': self.current_volume,
                    'price': self.current_price
                }
                self.api_client.record_sale(sale_data)
            except Exception as e:
                logger.error(f"Failed to record sale: {e}")
        
        self.filling_complete.emit()
        logger.info(f"Filling completed. Pulses: {self.pulse_count}/{self.target_pulses}")
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_filling()
        self.hardware.cleanup()

class VideoThread(QThread):
    frame_ready = pyqtSignal(QImage)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.mutex = QMutex()
        
    def run(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                logger.error("Failed to open video file")
                return
                
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video
                    continue
                
                with QMutexLocker(self.mutex):
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    
                    image = QImage(rgb_frame.data.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
                    image = image.copy()
                    
                    self.frame_ready.emit(image)
                    
                time.sleep(0.033)  # ~30 FPS
                
            cap.release()
            
        except Exception as e:
            logger.error(f"Error in video thread: {e}")
            
    def cleanup(self):
        """Clean up thread resources"""
        self.stop()
        self.wait()
    
    def stop(self):
        """Stop the thread safely"""
        with QMutexLocker(self.mutex):
            self.running = False

class SensorThread(QThread):
    sensor_updated = pyqtSignal(dict)
    
    def __init__(self, esp32_ip):
        super().__init__()
        self.config = ConfigManager()
        self.api_client = APIClient()
        self.esp32_ip = esp32_ip
        self.running = True
        self._last_successful_data = None
        

    def run(self):
        """Main thread loop with proper error handling"""
        while self.running:
            try:
                # Get sensor data from ESP32
                data = self._get_sensor_data()
                
                if data:
                    # Update last successful data
                    self._last_successful_data = data
                    
                    # Send to backend
                    self._send_to_backend(data)
                    
                    # Emit signal with new data
                    self.sensor_updated.emit(data)
                else:
                    # If failed to get new data, use last known good data
                    if self._last_successful_data:
                        self.sensor_updated.emit({
                            **self._last_successful_data,
                            'stale': True  # Indicate data is not fresh
                        })
                    else:
                        self.sensor_updated.emit({'error': True})
                        
            except Exception as e:
                logger.error(f"Error in sensor thread: {e}")
                self.sensor_updated.emit({'error': True})
            
            # Wait before next update
            time.sleep(self.config.app_config.update_interval)
    
    def _get_sensor_data(self) -> dict:
        """Get sensor data from ESP32 with proper error handling"""
        try:
            response = requests.get(
                f"http://{self.config.hardware_config.esp32_ip}:{self.config.hardware_config.esp32_port}/data",
                timeout=self.config.api_config.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            
            logger.warning(f"Failed to get sensor data: HTTP {response.status_code}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ESP32 connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting sensor data: {e}")
            return None
    
    def _send_to_backend(self, data: dict) -> None:
        """Send sensor data to backend"""
        try:
            quality_data = {
                'tds_level': data.get('tds', 0),
                'ph_level': data.get('ph', 7),
                'water_level': data.get('water_level', 0)
            }
            
            success = self.api_client.record_quality(quality_data)
            if not success:
                logger.warning("Failed to send quality data to backend")
                
        except Exception as e:
            logger.error(f"Error sending data to backend: {e}")
    
    def cleanup(self):
        """Clean up thread resources"""
        self.stop()
        self.wait()
    
    def stop(self):
        """Stop the thread safely"""
        self.running = False

class WaterButton(QPushButton):
    def __init__(self, size_text, price_text, image_path, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(150, 150)
        self.setCheckable(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        icon_container = QLabel()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 5px;
        """)
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_container.setPixmap(scaled_pixmap)
        icon_container.setAlignment(Qt.AlignCenter)
        
        size_label = QLabel(f"{size_text}\n{price_text}")
        size_label.setAlignment(Qt.AlignCenter)
        size_label.setStyleSheet("""
            color: #2C3E50;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
        """)
        
        layout.addWidget(icon_container, alignment=Qt.AlignCenter)
        layout.addWidget(size_label, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
            WaterButton {
                background-color: #F8F9FA;
                border-radius: 15px;
                border: 2px solid #E9ECEF;
            }
            WaterButton:checked {
                background-color: #4EA8DE;
                border: 2px solid #5390D9;
            }
            WaterButton:checked QLabel {
                color: white;
            }
            WaterButton:hover {
                background-color: #E9ECEF;
                border: 2px solid #DEE2E6;
            }
        """)

class MonitoringWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(150)
        
        self.setup_ui()
        self.setup_sensor_thread()
        
        # Register for cleanup if parent is WaterSustainabilityApp
        if isinstance(parent, WaterSustainabilityApp):
            parent.register_cleanup(self)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(layout)
        
        title = QLabel("Water Quality Monitoring")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            font-family: 'Segoe UI', Arial;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        monitor_container = QWidget()
        monitor_container.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 15px;
            border: 2px solid #E9ECEF;
            padding: 10px;
        """)
        
        monitor_layout = QHBoxLayout(monitor_container)
        monitor_layout.setContentsMargins(8, 4, 8, 4)
        
        self.ph_widget = self.create_monitor_display("pH Value")
        self.tds_widget = self.create_monitor_display("TDS Value")
        
        monitor_layout.addWidget(self.ph_widget)
        monitor_layout.addWidget(self.tds_widget)
        
        layout.addWidget(title)
        layout.addWidget(monitor_container)

    def setup_sensor_thread(self):
        try:
            self.sensor_thread = SensorThread(self.config.hardware_config.esp32_ip)
            self.sensor_thread.sensor_updated.connect(self.update_sensor_display)
            self.sensor_thread.start()
        except Exception as e:
            logger.error(f"Failed to setup sensor thread: {e}")
            self.update_sensor_display({'error': True})

    def create_monitor_display(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2C3E50;
            padding: 2px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel("Not Connected")
        value_label.setStyleSheet("""
            background-color: white;
            padding: 8px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
border: 1px solid #E9ECEF;
        """)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Store the value label reference
        if title == "pH Value":
            self.ph_value = value_label
        else:
            self.tds_value = value_label
        
        return widget

    def update_sensor_display(self, data):
        """Update display with sensor data"""
        try:
            if hasattr(self, 'ph_value') and hasattr(self, 'tds_value'):
                if 'error' in data:
                    self.ph_value.setText("Not Connected")
                    self.tds_value.setText("Not Connected")
                else:
                    ph_value = data.get('ph', 'Error')
                    tds_value = data.get('tds', 'Error')
                    self.ph_value.setText(f"{ph_value}")
                    self.tds_value.setText(f"{tds_value}")
        except Exception as e:
            logger.error(f"Error updating sensor display: {e}")
    
    def cleanup(self):
        """Clean up widget resources"""
        if hasattr(self, 'sensor_thread'):
            logger.debug("Cleaning up sensor thread")
            self.sensor_thread.cleanup()

class MachineWidget(QWidget):
    filling_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)
        
        # Initialize water controller
        self.water_controller = WaterController()
        self.water_controller.update_progress.connect(self.update_progress)
        self.water_controller.filling_complete.connect(self.complete_filling)
        self.water_controller.error_occurred.connect(self.handle_error)
        
        # Initialize UI state
        self.progress = 0
        self.is_filling = False
        self.progress_segments = 18
        
        self.setup_layout()
        
        # Register for cleanup if parent is WaterSustainabilityApp
        if isinstance(parent, WaterSustainabilityApp):
            parent.register_cleanup(self)

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        layout.addWidget(self.create_progress_container())
        layout.addWidget(self.create_machine_display())

    def create_progress_container(self):
        progress_container = QWidget()
        progress_container.setStyleSheet("""
            background-color: #2C3E50;
            border-radius: 15px;
            padding: 10px;
        """)
        
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(10, 5, 10, 5)
        
        self.progress_indicator = QLabel("█")
        self.progress_indicator.setStyleSheet("color: #2ECC71; font-size: 24px;")
        
        self.progress_bar = QLabel("▬" * self.progress_segments)
        self.progress_bar.setStyleSheet("color: white; font-size: 16px;")
        
        progress_layout.addWidget(self.progress_indicator)
        progress_layout.addWidget(self.progress_bar, 1)
        
        return progress_container

    def create_machine_display(self):
        machine_display = QWidget()
        machine_display.setStyleSheet("""
            background-color: #2C3E50;
            border-radius: 15px;
            padding: 10px;
        """)
        
        machine_layout = QVBoxLayout(machine_display)
        machine_layout.setSpacing(5)
        machine_layout.setContentsMargins(10, 5, 10, 5)
        
        self.machine_image = QLabel()
        self.machine_image.setFixedSize(80, 80)
        self.machine_image.setAlignment(Qt.AlignCenter)
        self.machine_image.setStyleSheet("background: transparent;")
        
        if os.path.exists("5.png"):
            machine_pixmap = QPixmap("5.png")
            scaled_machine = machine_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.machine_image.setPixmap(scaled_machine)
        
        self.start_button = QPushButton("Start Filling")
        self.start_button.setFixedSize(150, 40)
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                border: none;
            }
            QPushButton:disabled {
                background-color: #95A5A6;
            }
            QPushButton:hover:!disabled {
                background-color: #27AE60;
            }
        """)
        
        self.start_button.clicked.connect(self.start_filling_animation)
        
        machine_layout.addWidget(self.machine_image, alignment=Qt.AlignCenter)
        machine_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        
        return machine_display

    def start_filling_animation(self):
        """Start the water filling process"""
        if not self.is_filling and hasattr(self, 'selected_size'):
            success = self.water_controller.start_filling(self.selected_size)
            if success:
                self.is_filling = True
                self.progress = 0
                self.start_button.setEnabled(False)
                self.start_button.setText("Filling...")
                self.progress_indicator.setStyleSheet("color: #E74C3C; font-size: 24px;")

    def update_progress(self, progress):
        """Update progress bar visualization"""
        try:
            self.progress = progress
            filled = "█" * (progress * self.progress_segments // 100)
            empty = "▬" * (self.progress_segments - (progress * self.progress_segments // 100))
            self.progress_bar.setText(filled + empty)
        except Exception as e:
            logger.error(f"Error updating progress: {e}")

    def complete_filling(self):
        """Handle completion of filling process"""
        try:
            self.is_filling = False
            self.start_button.setEnabled(True)
            self.start_button.setText("Start Filling")
            self.progress_indicator.setStyleSheet("color: #2ECC71; font-size: 24px;")
            self.filling_completed.emit()
        except Exception as e:
            logger.error(f"Error completing filling: {e}")

    def handle_error(self, error_msg: str):
        """Handle errors during filling process"""
        logger.error(f"Filling error: {error_msg}")
        self.complete_filling()
        # You might want to add UI feedback for errors here

    def cleanup(self):
        """Clean up widget resources"""
        if hasattr(self, 'water_controller'):
            logger.debug("Cleaning up water controller")
            self.water_controller.cleanup()

class WaterSustainabilityApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._cleanup_handlers = []
        self.config = ConfigManager()
        self.payment_manager = PaymentManager()
        self.initUI()

    def start_payment(self, size):
        """Initialize payment process"""
        volume = WATER_VOLUMES.get(size)
        if not volume:
            return
            
        # Convert price string to integer (remove "Rp. " and ".")
        price_str = volume.price.replace("Rp. ", "").replace(".", "")
        amount = int(price_str)
        
        try:
            payment_dialog = PaymentDialog(
                self.payment_manager, 
                amount,
                volume.display_name,
                self
            )
            payment_dialog.payment_completed.connect(
                lambda success: self.handle_payment_complete(success, size)
            )
            payment_dialog.exec_()
        except Exception as e:
            logger.error(f"Error starting payment: {e}")

    def handle_payment_complete(self, success: bool, size: str):
        """Handle payment completion"""
        if success:
            # Start water dispensing
            self.machine_widget.selected_size = size
            self.machine_widget.start_filling_animation()
        else:
            # Show payment failed message
            QMessageBox.warning(
                self,
                "Payment Failed",
                "Payment was not completed. Please try again."
            )

    def register_cleanup(self, handler):
        """Register objects that need cleanup"""
        self._cleanup_handlers.append(handler)
        logger.debug(f"Registered cleanup handler: {handler.__class__.__name__}")

    def initUI(self):
        self.setWindowTitle("Innovative Aqua Solution")
        self.setStyleSheet("background-color: #E3F2FD;")
        
        screen = QApplication.desktop().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.setMinimumSize(1366, 768)
        self.resize(width, height)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Left panel setup
        left_panel = QWidget()
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        
        # Video container
        video_container = self.create_video_container()
        left_layout.addWidget(video_container, 7)
        
        # Monitoring widget
        monitoring_widget = MonitoringWidget(self)
        left_layout.addWidget(monitoring_widget, 3)
        
        # Right panel setup
        right_panel = self.create_right_panel()
        
        content_layout.addWidget(left_panel, 7)
        content_layout.addWidget(right_panel, 0)
        
        main_layout.addWidget(content)
        
        self.setup_video()

    def create_video_container(self):
        video_container = QWidget()
        video_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        video_container.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 20px;
            border: 2px solid #E9ECEF;
            padding: 10px;
        """)
        
        video_layout = QVBoxLayout(video_container)
        
        self.video_label = QLabel()
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setMaximumSize(1280, 720)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #E9ECEF;
                border-radius: 10px;
            }
        """)
        
        video_layout.addWidget(self.video_label)
        return video_container

    def create_right_panel(self):
        right_panel = QWidget()
        right_panel.setFixedWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Water selection section
        selection_widget = QWidget()
        selection_widget.setStyleSheet("""
            background-color: #F8F9FA;
            border-radius: 20px;
            border: 2px solid #E9ECEF;
            padding: 20px;
        """)
        
        selection_layout = QVBoxLayout(selection_widget)
        
        selection_title = QLabel("Select Water Size")
        selection_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            font-family: 'Segoe UI', Arial;
        """)
        selection_title.setAlignment(Qt.AlignCenter)
        
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(10)
        
        self.size_buttons = []
        button_positions = [
            ("100 ml", "1.png", 0, 0),
            ("350 ml", "2.png", 0, 1),
            ("600 ml", "3.png", 1, 0),
            ("1 Liter", "4.png", 1, 1)
        ]
        
        for size, image_path, row, col in button_positions:
            volume = WATER_VOLUMES.get(size)
            if volume and os.path.exists(image_path):
                btn = WaterButton(volume.name, volume.price, image_path)
                btn.clicked.connect(lambda checked, s=size: self.on_size_selected(s))
                buttons_grid.addWidget(btn, row, col)
                self.size_buttons.append(btn)
        
        selection_layout.addWidget(selection_title)
        selection_layout.addLayout(buttons_grid)
        selection_layout.addStretch()
        
        # Machine widget
        self.machine_widget = MachineWidget(self)
        
        right_layout.addWidget(selection_widget)
        right_layout.addWidget(self.machine_widget)
        right_layout.addStretch()
        
        return right_panel

    def setup_video(self):
        """Set up video thread with proper cleanup registration"""
        try:
            video_path = self.config.app_config.video_path
            if not os.path.exists(video_path):
                self.video_label.setText("Video not found")
                return
                
            self.video_thread = VideoThread(video_path)
            self.video_thread.frame_ready.connect(self.update_video_frame, Qt.QueuedConnection)
            self.register_cleanup(self.video_thread)
            self.video_thread.start()
            
        except Exception as e:
            logger.error(f"Error setting up video: {e}")
            self.video_label.setText(f"Error: {str(e)}")

    def update_video_frame(self, image):
        """Update video frame with proper error handling"""
        try:
            if not self.video_label or image.isNull():
                return
                
            label_size = self.video_label.size()
            if not label_size.isValid():
                return
                
            scaled_pixmap = QPixmap.fromImage(image).scaled(
                label_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            if not scaled_pixmap.isNull():
                self.video_label.setPixmap(scaled_pixmap)
                
        except Exception as e:
            logger.error(f"Error updating video frame: {e}")

    def on_size_selected(self, size):
        """Handle water size selection"""
        try:
            clicked_button = self.sender()
            for btn in self.size_buttons:
                if btn != clicked_button:
                    btn.setChecked(False)
            
            self.machine_widget.selected_size = size if clicked_button.isChecked() else None
            self.machine_widget.start_button.setEnabled(
                self.machine_widget.selected_size is not None
            )

            if clicked_button.isChecked():
                self.start_payment(size)


        except Exception as e:
            logger.error(f"Error in size selection: {e}")

    def resizeEvent(self, event):
        """Handle window resize events"""
        try:
            super().resizeEvent(event)
            if hasattr(self, 'video_label'):
                new_width = min(1280, int(self.width() * 0.6))
                new_height = min(720, int(self.height() * 0.6))
                self.video_label.setMinimumSize(new_width, new_height)
        except Exception as e:
            logger.error(f"Error in resize event: {e}")

    def closeEvent(self, event):
        """Handle application shutdown with proper cleanup"""
        logger.info("Application shutdown initiated")
        
        try:
            # Stop video thread if exists
            if hasattr(self, 'video_thread'):
                logger.debug("Stopping video thread")
                self.video_thread.cleanup()
            
            # Cleanup machine widget
            if hasattr(self, 'machine_widget'):
                logger.debug("Cleaning up machine widget")
                self.machine_widget.cleanup()
            
            # Run all registered cleanup handlers
            for handler in self._cleanup_handlers:
                try:
                    logger.debug(f"Running cleanup for: {handler.__class__.__name__}")
                    handler.cleanup()
                except Exception as e:
                    logger.error(f"Error during cleanup of {handler.__class__.__name__}: {e}")
            
            logger.info("Application cleanup completed successfully")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
            event.accept()  # Accept the close event even if cleanup fails
            
        finally:
            # Final cleanup attempt for GPIO
            if HARDWARE_AVAILABLE:
                try:
                    GPIO.cleanup()
                    logger.info("GPIO cleanup completed")
                except Exception as e:
                    logger.error(f"Final GPIO cleanup failed: {e}")

def create_app():
    """Create and initialize the application with proper error handling"""
    try:
        # Set up application-wide exception handling
        sys.excepthook = handle_exception
        
        app = QApplication(sys.argv)
        
        # Set application-wide font
        app.setFont(QFont('Segoe UI', 10))
        
        # Create and show main window
        window = WaterSustainabilityApp()
        window.show()
        
        return app.exec_()
    
    except Exception as e:
        logger.critical(f"Failed to create application: {e}")
        return 1

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle keyboard interrupt specially
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

if __name__ == '__main__':
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('vending_machine.log'),
                logging.StreamHandler()
            ]
        )
        
        # Start application
        sys.exit(create_app())
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        if HARDWARE_AVAILABLE:
            GPIO.cleanup()
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Critical application error: {e}")
        if HARDWARE_AVAILABLE:
            GPIO.cleanup()
        sys.exit(1)