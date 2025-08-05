import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)

while True:
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(f"Toroid Data: {data}")
        with open('toroid_log.txt', 'a') as f:
            f.write(f"{time.time()}: {data}\n")
    time.sleep(1)