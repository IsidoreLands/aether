# sensor_hook.py
#
# Description:
# This module provides the interface to the ferrocell sensor array. It is designed
# to be a "real-time clock" for the AetherOS, feeding non-deterministic, real-world
# physical data into the simulation.
#
# It runs in its own thread to continuously poll for data without blocking the main
# application. It can be run in 'mock_mode' for development without hardware.

import threading
import time
import random
import numpy as np

# Attempt to import the serial library, which is optional.
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

class FerrocellSensor:
    """
    Interface to ferrocell sensors for real-time sextet data.
    This class polls the sensor data in a background thread.
    """
    def __init__(self, mock_mode=True, port='/dev/ttyACM2', baud=9600):
        """
        Initializes the sensor.
        
        Args:
            mock_mode (bool): If True, generates simulated data. If False, attempts to
                              connect to real hardware via serial.
            port (str): The serial port for the hardware connection.
            baud (int): The baud rate for the serial connection.
        """
        self.mock_mode = mock_mode
        self.ser = None
        
        if not self.mock_mode:
            if SERIAL_AVAILABLE:
                try:
                    self.ser = serial.Serial(port, baud, timeout=1)
                    print(f"INFO: Hardware mode enabled. Connected to {port} at {baud} baud.")
                except Exception as e:
                    print(f"WARN: Could not connect to serial port {port}. Reason: {e}")
                    print("WARN: Falling back to mock_mode.")
                    self.mock_mode = True
            else:
                print("WARN: 'pyserial' library not found. Please install it (`pip install pyserial`) to use hardware mode.")
                print("WARN: Falling back to mock_mode.")
                self.mock_mode = True

        # The sextet dictionary holds the six core physical properties.
        self.sextet = {
            'resistance': 1e-9,
            'capacitance': 0.0,
            'permeability': 1.0,
            'magnetism': 0.0,
            'permittivity': 1.0,
            'dielectricity': 0.0
        }
        
        # Start the background thread for polling.
        self.thread = threading.Thread(target=self._poll_sensors, daemon=True)
        self.thread.start()
        print("INFO: FerrocellSensor thread started.")

    def _poll_sensors(self):
        """
        The main loop for the sensor polling thread. Updates the sextet values.
        """
        while True:
            if self.mock_mode:
                # Nondeterministic mock data based on time and random chaos.
                t = time.time()
                self.sextet['resistance'] = 1e-9 * (1 + np.sin(t * 0.2) * 0.1)
                self.sextet['capacitance'] = abs(np.cos(t * 0.5) * 0.5)
                self.sextet['permeability'] = 1.0 + random.uniform(-0.1, 0.1)
                self.sextet['magnetism'] = random.uniform(0.0, 0.2)
                self.sextet['permittivity'] = 1.0 + np.sin(t * 0.3) * 0.05
                self.sextet['dielectricity'] = random.uniform(0.0, 0.4)
            else:
                # Real hardware read (example; adapt to your sensor's protocol)
                if self.ser and self.ser.is_open:
                    try:
                        self.ser.write(b'READ_SEXTET\n')
                        data = self.ser.readline().decode().strip()
                        if data:
                            values = list(map(float, data.split(',')))
                            if len(values) == 6:
                                keys = ['resistance', 'capacitance', 'permeability', 'magnetism', 'permittivity', 'dielectricity']
                                self.sextet = dict(zip(keys, values))
                    except Exception as e:
                        print(f"ERROR: Failed to read from serial device: {e}")
            
            time.sleep(0.1)  # Poll rate; adjust for responsiveness.

    def get_sextet(self):
        """
        Provides a thread-safe copy of the latest sextet data.
        
        Returns:
            dict: A copy of the current sextet values.
        """
        return self.sextet.copy()

# Create a single, global instance of the sensor.
# This instance will be imported by other modules.
ferro_sensor = FerrocellSensor(mock_mode=True)

if __name__ == '__main__':
    # Standalone test for the sensor module.
    print("--- Running sensor_hook.py standalone test ---")
    print("This demonstrates the sensor polling in mock mode.")
    print("Press Ctrl+C to stop.")
    try:
        for i in range(5):
            time.sleep(1)
            current_sextet = ferro_sensor.get_sextet()
            print(f"Poll {i+1}: {current_sextet}")
        print("\nTest complete. Sensor thread continues in background.")
    except KeyboardInterrupt:
        print("\nTest stopped by user.")