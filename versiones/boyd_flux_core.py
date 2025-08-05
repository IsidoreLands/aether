#!/usr/bin/env python3

import numpy as np
import random

# Import the global sensor instance
from sensor_hook import ferro_sensor

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class FluxCore:
    """
    A fundamental unit of existence whose physics are governed by E-M theory.
    """
    def __init__(self, size=128):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.float32)
        
        # --- E-M Sextet Properties ---
        self.specific_energy = 100.0 # (Es) Represents total state (h + V^2/2/2g)
        self.thrust = 100.0          # (T) Force that adds energy
        self.drag = 95.0             # (D) Force that removes energy
        self.velocity = 1.0          # (V) A measure of the core's speed/activity
        self.weight = 10.0           # (W) Inertia or resistance to change
        self.load_factor = 1.0       # (n) Multiplier for energy cost during maneuvers

        self.memory_patterns = []
        self.context_embeddings = {}
        self.anomaly = None

        self._sync_environmental_factors()

    def _sync_environmental_factors(self):
        """Sync with sensor data."""
        sensor_data = ferro_sensor.get_sextet()
        self.environment_factor = np.clip(sensor_data.get('permeability', 1.0), 0.5, 1.5)

    def maneuver(self, thrust_change, load_factor_change):
        """Perturb the core using E-M maneuver."""
        self._sync_environmental_factors()
        
        self.thrust += thrust_change
        self.load_factor = max(1.0, self.load_factor + load_factor_change)

        # Drag increases with the square of the load factor
        self.drag = 95.0 * (self.load_factor**2) * self.environment_factor
        
        self._update_energy_state()
        self._update_memory(f"Maneuver: T={thrust_change}, n={load_factor_change}")

    def stabilize(self):
        """Stabilize the core."""
        self.thrust *= 0.95 
        self.load_factor *= 0.9
        self.load_factor = max(1.0, self.load_factor)
        
        self.drag = 95.0 * (self.load_factor**2) * self.environment_factor
        
        self._update_energy_state()
        self._update_memory("Stabilize")

    def _update_energy_state(self):
        """Update energy state."""
        specific_excess_power = ((self.thrust * self.environment_factor) - self.drag) * self.velocity / self.weight
        
        self.specific_energy += specific_excess_power
        self.specific_energy = max(0, self.specific_energy)  # Prevent negative energy
        
        self.velocity = np.sqrt(max(0, 2 * 9.81 * (self.specific_energy - 0)) ) * 0.1  # Simplified V = sqrt(2g * Es) assuming h=0
        
        # Update grid
        center_brightness = np.clip(self.specific_energy / 200.0, 0, 1)
        self.grid = np.zeros((self.size, self.size), dtype=np.float32)
        if CV2_AVAILABLE:
            cv2.circle(self.grid, (self.size//2, self.size//2), int(self.size/4), center_brightness, -1)
        else:
            # Mock without cv2
            self.grid[self.size//4:self.size*3//4, self.size//4:self.size*3//4] = center_brightness

    def _update_memory(self, change):
        """Record change to memory."""
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100: self.memory_patterns.pop(0)

    def display(self):
        """Display the core's state."""
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"SPECIFIC ENERGY (Es): {self.specific_energy:.2f}\n"
                f"E-M SEXTET: T={self.thrust:.2f}, D={self.drag:.2f}, V={self.velocity:.2f}, W={self.weight:.2f}, n={self.load_factor:.2f}\n"
                f"CONTEXTUS:\n{context_str}")

class Intellectus(FluxCore):
    """A specialized E-M core with enhanced learning/adaptation."""
    def __init__(self, architecture='TRANSFORMER', size=128):
        super().__init__(size)
        self.architecture = architecture
        if self.architecture == 'TRANSFORMER':
            self.weight = 8.0 # Lighter, more agile

    def maneuver(self, thrust_change, load_factor_change):
        super().maneuver(thrust_change * 1.2, load_factor_change)