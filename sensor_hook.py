# sensor_hook.py
#
# Description:
# This module provides the interface to the ferrocell sensor array. It now includes
# both the sextet data poller and a camera feed manager for visual grounding.
# It runs in its own thread to continuously poll for data without blocking the main
# application.

import threading
import time
import random
import numpy as np

# Attempt to import optional hardware-specific libraries
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import cv2
    from picamera import PiCamera
    from picamera.array import PiRGBArray
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

class FerrocellSensor:
    """
    Interface to ferrocell sensors for real-time sextet and visual data.
    This class polls all sensor data in a background thread.
    """
    def __init__(self, mock_mode=True, port='/dev/ttyACM2', baud=9600, resolution=(128, 128)):
        self.mock_mode = mock_mode
        self.resolution = resolution
        self.ser = None
        self.camera = None
        self.raw_capture = None

        # --- Hardware Initialization ---
        if not self.mock_mode:
            # Initialize Serial
            if SERIAL_AVAILABLE:
                try:
                    self.ser = serial.Serial(port, baud, timeout=1)
                    print(f"INFO: Hardware mode enabled. Connected to {port} at {baud} baud.")
                except Exception as e:
                    print(f"WARN: Could not connect to serial port {port}. Reason: {e}")
            else:
                print("WARN: 'pyserial' not found. Sextet will be mocked.")

            # Initialize Camera
            if CAMERA_AVAILABLE:
                try:
                    self.camera = PiCamera()
                    self.camera.resolution = self.resolution
                    self.raw_capture = PiRGBArray(self.camera, size=self.resolution)
                    time.sleep(2) # Allow camera to warm up
                    print(f"INFO: PiCamera initialized at {self.resolution} resolution.")
                except Exception as e:
                    print(f"WARN: Could not initialize PiCamera. Reason: {e}")
                    if self.camera: self.camera.close()
                    self.camera = None
            else:
                print("WARN: 'picamera' or 'opencv-python' not found. Visual grid will be mocked.")

        # --- Data Attributes ---
        self.sextet = {'resistance': 1e-9, 'capacitance': 0.0, 'permeability': 1.0,
                       'magnetism': 0.0, 'permittivity': 1.0, 'dielectricity': 0.0}
        self.visual_grid = np.zeros(self.resolution, dtype=np.float32)

        # Start the background thread for polling.
        self.thread = threading.Thread(target=self._poll_sensors, daemon=True)
        self.thread.start()
        print("INFO: FerrocellSensor thread started.")

    def _poll_sensors(self):
        """The main loop for the sensor polling thread. Updates all sensor data."""
        while True:
            # --- Poll Sextet Data ---
            if self.ser and self.ser.is_open:
                # Real hardware read
                try:
                    self.ser.write(b'READ_SEXTET\n')
                    data = self.ser.readline().decode().strip()
                    if data and len(data.split(',')) == 6:
                        values = list(map(float, data.split(',')))
                        keys = list(self.sextet.keys())
                        self.sextet = dict(zip(keys, values))
                except Exception as e:
                    print(f"ERROR: Failed to read from serial device: {e}")
            else:
                # Mock sextet data
                t = time.time()
                self.sextet['permeability'] = 0.5 + (np.sin(t * 0.1) * 0.5) # Make permeability vary for grounding
                self.sextet['magnetism'] = random.uniform(0.0, 0.2)

            # --- Poll Visual Data ---
            if self.camera:
                # Real camera capture
                try:
                    self.camera.capture(self.raw_capture, format="bgr", use_video_port=True)
                    image = self.raw_capture.array
                    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    self.visual_grid = gray_image / 255.0 # Normalize to 0-1
                    self.raw_capture.truncate(0)
                except Exception as e:
                    print(f"ERROR: Failed to capture from PiCamera: {e}")
            else:
                # Mock visual data (e.g., a moving sine wave pattern)
                x = np.linspace(-np.pi, np.pi, self.resolution[1])
                y = np.linspace(-np.pi, np.pi, self.resolution[0])
                xx, yy = np.meshgrid(x, y)
                t = time.time()
                self.visual_grid = 0.5 * (1 + np.sin(xx * 2 + t) * np.cos(yy * 2 + t))

            time.sleep(0.1)  # Poll rate for all sensors.

    def get_sextet(self):
        """Provides a thread-safe copy of the latest sextet data."""
        return self.sextet.copy()

    def get_visual_grid(self):
        """Provides a thread-safe copy of the latest visual grid data."""
        return self.visual_grid.copy() if self.visual_grid is not None else None

# Create a single, global instance of the sensor.
ferro_sensor = FerrocellSensor(mock_mode=True, resolution=(128, 128))

if __name__ == '__main__':
    print("--- Running sensor_hook.py standalone test (v4) ---")
    print("Press Ctrl+C to stop.")
    try:
        for i in range(5):
            time.sleep(1)
            sextet = ferro_sensor.get_sextet()
            grid = ferro_sensor.get_visual_grid()
            print(f"\nPoll {i+1}:")
            print(f"  Sextet: {sextet}")
            if grid is not None:
                print(f"  Visual Grid: shape={grid.shape}, mean={np.mean(grid):.3f}, std={np.std(grid):.3f}")
        print("\nTest complete.")
    except KeyboardInterrupt:
        print("\nTest stopped by user.")