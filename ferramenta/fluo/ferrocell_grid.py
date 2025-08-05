import serial
import time
from picamera import PiCamera  # For OV2640, use arducam if SPI
# For multispectral upgrade: import adafruit_as726x  # I2C sensor

ser = serial.Serial('/dev/ttyACM0', 9600)  # Arduino port
camera = PiCamera()  # Or arducam setup

def capture_image(filename='ferrocell.jpg'):
    camera.start_preview()
    time.sleep(2)
    camera.capture(filename)
    camera.stop_preview()
    print(f"Image captured: {filename}")

# Multispectral read example (if upgraded)
# i2c = board.I2C()
# sensor = adafruit_as726x.AS726x_I2C(i2c)
# def read_multispectral():
#     return sensor.read_channel()  # Channels for wavelengths

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"From Arduino: {data}")
        capture_image()  # Sync with readings
    time.sleep(1)