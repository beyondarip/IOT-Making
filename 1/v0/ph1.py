import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import statistics

class PHMeter:
    def __init__(self, channel=0):
        """
        Inisialisasi sensor pH dengan koreksi kalibrasi
        
        Parameter:
        - channel: Saluran ADC yang digunakan (default: 0)
        """
        # Setup I2C untuk komunikasi dengan ADS1115
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Buat objek ADS1115
        self.ads = ADS.ADS1115(self.i2c)
        
        # Pilih channel yang akan digunakan
        self.channel = AnalogIn(self.ads, channel)
        
        # Parameter kalibrasi
        self.ph_4_voltage = None
        self.ph_9_voltage = None
        
        # Konstanta kalibrasi
        self.CALIBRATION_TOLERANCE = 0.1  # Toleransi selisih voltage
    
    def calibrate(self, ph_buffer):
        """
        Metode kalibrasi sensor pH dengan validasi
        
        Parameter:
        - ph_buffer: Buffer pH (4 atau 9)
        
        Return:
        - List voltage yang terukur
        """
        print(f"Kalibrasi pH {ph_buffer}")
        print("Pastikan sensor benar-benar terendam")
        print("Tunggu 60 detik untuk stabilisasi...")
        
        # Ambil multiple readings untuk akurasi
        voltage_readings = []
        for _ in range(10):
            voltage = self.channel.voltage
            voltage_readings.append(voltage)
            time.sleep(1)
        
        # Hitung statistik
        median_voltage = statistics.median(voltage_readings)
        std_dev = statistics.stdev(voltage_readings)
        
        print(f"Median Voltage: {median_voltage:.3f} V")
        print(f"Standar Deviasi: {std_dev:.3f} V")
        
        # Validasi kestabilan
        if std_dev > self.CALIBRATION_TOLERANCE:
            raise ValueError("Kalibrasi tidak stabil. Periksa koneksi sensor.")
        
        # Simpan voltage kalibrasi
        if ph_buffer == 4:
            self.ph_4_voltage = median_voltage
        elif ph_buffer == 9:
            self.ph_9_voltage = median_voltage
        
        return voltage_readings
    
    def calculate_ph(self):
        """
        Hitung nilai pH dengan metode interpolasi linear
        
        Return:
        - Nilai pH terukur
        """
        # Pastikan kalibrasi sudah lengkap
        if not (self.ph_4_voltage and self.ph_9_voltage):
            raise ValueError("Kalibrasi belum selesai!")
        
        # Baca voltage saat ini
        current_voltage = self.channel.voltage
        
        # Hitung slope (gradien)
        # Rumus: slope = (pH2 - pH1) / (V2 - V1)
        slope = (9 - 4) / (self.ph_9_voltage - self.ph_4_voltage)
        
        # Hitung intersep
        # y = mx + b → b = y - mx
        intersep = 4 - (slope * self.ph_4_voltage)
        
        # Hitung pH
        ph_value = (slope * current_voltage) + intersep
        
        return round(ph_value, 2)
    
    def read_ph(self, samples=10):
        """
        Pembacaan pH dengan multiple sampling
        
        Parameter:
        - samples: Jumlah sampel
        
        Return:
        - Rata-rata pH dengan filter outliers
        """
        ph_readings = []
        
        for _ in range(samples):
            try:
                ph = self.calculate_ph()
                ph_readings.append(ph)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error pembacaan: {e}")
        
        # Filter outliers menggunakan IQR
        if len(ph_readings) > 4:
            q1 = statistics.quantiles(ph_readings)[0]
            q3 = statistics.quantiles(ph_readings)[2]
            iqr = q3 - q1
            filtered_readings = [
                x for x in ph_readings 
                if (q1 - 1.5 * iqr) <= x <= (q3 + 1.5 * iqr)
            ]
            
            return round(statistics.mean(filtered_readings), 2)
        
        return round(statistics.mean(ph_readings), 2)

def main():
    """
    Fungsi utama untuk kalibrasi dan pembacaan pH
    """
    try:
        # Inisialisasi pH meter
        ph_meter = PHMeter()
        
        print("KALIBRASI PH 4")
        ph_meter.calibrate(4)
        
        print("\nKALIBRASI PH 9")
        ph_meter.calibrate(9)
        
        # Loop pembacaan pH
        while True:
            try:
                ph_value = ph_meter.read_ph()
                print(f"Nilai pH: {ph_value}")
                time.sleep(2)
            except Exception as e:
                print(f"Kesalahan pembacaan: {e}")
    
    except Exception as e:
        print(f"Kesalahan: {e}")

if __name__ == "__main__":
    main()