import serial
import time
import numpy as np
import threading  # For concurrent reading if multiple Arduinos
import json  # For logging baselines

# Config: Serial ports for each setup's Arduino (adjust as per hardware)
TOROID_PORT = '/dev/ttyACM0'  # Toroid Arduino
SOLENOID_PORT = '/dev/ttyACM1'  # Solenoid Arduino
FERROCELL_PORT = '/dev/ttyACM2'  # Ferrocell Arduino (for grid sensors, e.g., photoresistors/camera proxy)

# Calibration parameters
SAMPLE_COUNT = 100  # Samples for baseline averaging
SAMPLE_INTERVAL = 0.5  # Seconds between samples
BASELINE_FILE = 'ferrocell_baseline.json'  # Save/load baselines

class SensorReader:
    def __init__(self, port, baud=9600):
        self.ser = serial.Serial(port, baud, timeout=1)
        self.data = {'hall': 0.0, 'lcr': {'inductance': 0.0, 'capacitance': 0.0, 'resistance': 0.0}}

    def read_data(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()
            if line.startswith('HALL:'):
                parts = line.split(',')
                self.data['hall'] = float(parts[0].split(':')[1])
                lcr_str = parts[1].split(':')[1]  # Assume "LCR:inductance,capacitance,resistance"
                lcr_vals = lcr_str.split(',')
                self.data['lcr']['inductance'] = float(lcr_vals[0])
                self.data['lcr']['capacitance'] = float(lcr_vals[1])
                self.data['lcr']['resistance'] = float(lcr_vals[2])
        return self.data

def calibrate_baseline(reader, setup_name):
    print(f"Calibrating {setup_name}... (No external fields; {SAMPLE_COUNT} samples)")
    hall_samples = []
    inductance_samples = []
    capacitance_samples = []
    resistance_samples = []
    
    for _ in range(SAMPLE_COUNT):
        data = reader.read_data()
        hall_samples.append(data['hall'])
        inductance_samples.append(data['lcr']['inductance'])
        capacitance_samples.append(data['lcr']['capacitance'])
        resistance_samples.append(data['lcr']['resistance'])
        time.sleep(SAMPLE_INTERVAL)
    
    baseline = {
        'magnetism_zero': np.mean(hall_samples),
        'permeability_base': np.mean(inductance_samples) / (np.mean(hall_samples) + 1e-6),  # Derived: L ~ μ (simplified)
        'capacitance_zero': np.mean(capacitance_samples),
        'resistance_zero': np.mean(resistance_samples),
        'permittivity_base': 1.0 / (np.mean(capacitance_samples) + 1e-6),  # Derived approximation
        'dielectricity_base': np.mean(resistance_samples) * np.mean(capacitance_samples)  # RC time constant proxy
    }
    return baseline

def merge_baselines(toroid_base, solenoid_base):
    # Average baselines from toroid/solenoid (same ferrofluid assumption)
    merged = {}
    for key in toroid_base:
        merged[key] = (toroid_base[key] + solenoid_base[key]) / 2
    return merged

def apply_to_ferrocell(ferro_reader, baseline):
    # Real-time adjustment: Subtract baseline from current readings
    data = ferro_reader.read_data()
    adjusted = {
        'magnetism': data['hall'] - baseline['magnetism_zero'],
        'permeability': (data['lcr']['inductance'] / (data['hall'] + 1e-6)) - baseline['permeability_base'],
        'capacitance': data['lcr']['capacitance'] - baseline['capacitance_zero'],
        'resistance': data['lcr']['resistance'] - baseline['resistance_zero'],
        'permittivity': 1.0 / (data['lcr']['capacitance'] + 1e-6) - baseline['permittivity_base'],
        'dielectricity': data['lcr']['resistance'] * data['lcr']['capacitance'] - baseline['dielectricity_base']
    }
    return adjusted

def save_baseline(baseline, filename=BASELINE_FILE):
    with open(filename, 'w') as f:
        json.dump(baseline, f)
    print(f"Baseline saved to {filename}")

def load_baseline(filename=BASELINE_FILE):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None

# Main calibration and real-time loop
if __name__ == '__main__':
    toroid_reader = SensorReader(TOROID_PORT)
    solenoid_reader = SensorReader(SOLENOID_PORT)
    ferro_reader = SensorReader(FERROCELL_PORT)
    
    # Initial calibration (run once or on demand)
    toroid_base = calibrate_baseline(toroid_reader, "Toroid")
    solenoid_base = calibrate_baseline(solenoid_reader, "Solenoid")
    merged_base = merge_baselines(toroid_base, solenoid_base)
    save_baseline(merged_base)
    
    # Real-time baseline application for ferrocell
    print("Starting real-time ferrocell monitoring with baselines...")
    while True:
        adjusted_data = apply_to_ferrocell(ferro_reader, merged_base)
        print(f"Adjusted Ferrocell Data: {adjusted_data}")
        time.sleep(1)  # Adjust for update rate