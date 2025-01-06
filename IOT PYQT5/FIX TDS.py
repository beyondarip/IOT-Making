import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Initialize I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Set gain (bisa disesuaikan: 2/3, 1, 2, 4, 8, 16)
ads.gain = 1

# Gunakan channel A0 
chan = AnalogIn(ads, ADS.P0)

# TDS Calibration Constants
VREF = 5.0  # Sensor reference voltage
TDS_FACTOR = 0.5  # TDS conversion factor
TEMPERATURE = 25.0  # Suhu air dalam celsius

def calculate_tds(voltage, temperature=25.0):
    # Kompensasi suhu
    temp_coefficient = 1.0 + 0.02 * (temperature - 25.0)
    
    # Hitung TDS dengan kompensasi suhu
    tds_value = ((133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5) / temp_coefficient
    return tds_value

try:
    while True:
        # Baca voltage
        voltage = chan.voltage
        
        # Hitung TDS
        tds_value = calculate_tds(voltage, TEMPERATURE)
        
        print(f"Voltage: {voltage:.3f}V | TDS Value: {tds_value:.0f} ppm")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram dihentikan")