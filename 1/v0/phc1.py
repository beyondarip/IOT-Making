import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class PHMeter:
    def __init__(self):
        """
        Inisialisasi sensor pH dengan ADS1115
        pip install adafruit-circuitpython-ads1x15
        """
        # Inisialisasi I2C dan ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        
        # Set gain untuk mendapatkan pembacaan yang lebih presisi
        self.ads.gain = 1
        
        # Konfigurasi pin analog untuk sensor pH
        self.ph_channel = AnalogIn(self.ads, ADS.P0)
        
        # Variabel untuk kalibrasi
        self.ph4_voltage = 0
        self.ph9_voltage = 0
        self.slope = 0
        self.intercept = 0

    def read_voltage(self):
        """
        Membaca tegangan dari sensor pH
        
        Returns:
        float: Tegangan yang terbaca
        """
        return self.ph_channel.voltage

    def calibrate(self, calibration_type):
        """
        Proses Kalibrasi Sensor pH
        
        Args:
        calibration_type (str): Tipe kalibrasi ('ph4' atau 'ph9')
        
        Proses Kalibrasi:
        1. pH 4 Buffer (Asam):
           - Celupkan elektroda ke larutan buffer pH 4
           - Tunggu hingga pembacaan stabil
           - Catat tegangan
        
        2. pH 9 Buffer (Basa):
           - Celupkan elektroda ke larutan buffer pH 9
           - Tunggu hingga pembacaan stabil
           - Catat tegangan
        
        3. Hitung Slope dan Intercept:
           - Gunakan metode linear regression
           - pH = Slope * Voltage + Intercept
        """
        print(f"Memulai kalibrasi {calibration_type}")
        print("Pastikan elektroda dalam kondisi bersih")
        print("Celupkan ke larutan buffer yang sesuai")
        
        input("Tekan Enter setelah elektroda dicelupkan...")
        
        # Pembacaan tegangan selama 10 detik dan ambil rata-rata
        readings = []
        for _ in range(10):
            readings.append(self.read_voltage())
            time.sleep(1)
        
        avg_voltage = sum(readings) / len(readings)
        
        if calibration_type == 'ph4':
            self.ph4_voltage = avg_voltage
            print(f"Tegangan pH 4: {self.ph4_voltage:.3f} V")
        elif calibration_type == 'ph9':
            self.ph9_voltage = avg_voltage
            print(f"Tegangan pH 9: {self.ph9_voltage:.3f} V")
        
        # Hitung slope dan intercept setelah kedua titik kalibrasi
        if self.ph4_voltage and self.ph9_voltage:
            self.slope = (9 - 4) / (self.ph9_voltage - self.ph4_voltage)
            self.intercept = 4 - (self.slope * self.ph4_voltage)
            
            print("\n--- Hasil Kalibrasi ---")
            print(f"Slope: {self.slope:.4f}")
            print(f"Intercept: {self.intercept:.4f}")

    def read_ph(self):
        """
        Membaca nilai pH berdasarkan tegangan
        
        Returns:
        float: Nilai pH yang telah dikalibrasi
        
        Catatan:
        - Pastikan kalibrasi dilakukan sebelum membaca pH
        - Memerlukan slope dan intercept dari kalibrasi
        """
        if not (self.slope and self.intercept):
            raise ValueError("Lakukan kalibrasi terlebih dahulu!")
        
        voltage = self.read_voltage()
        ph_value = (self.slope * voltage) + self.intercept
        return ph_value

def main():
    # Contoh penggunaan
    ph_meter = PHMeter()
    
    # Kalibrasi
    ph_meter.calibrate('ph4')
    time.sleep(2)
    ph_meter.calibrate('ph9')
    
    # Membaca pH
    try:
        while True:
            ph = ph_meter.read_ph()
            print(f"Nilai pH: {ph:.2f}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Pembacaan pH dihentikan")

if __name__ == "__main__":
    main()