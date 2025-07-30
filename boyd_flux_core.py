# boyd_flux_core.py
#
# Description:
# An alternative implementation of the FluxCore based on John Boyd's
# Energy-Maneuverability (E-M) theory. This module redefines the core
# physics of the AetherOS to model energy dynamics from aeronautics.

import numpy as np
import random
import cv2

# Import the global sensor instance
from sensor_hook import ferro_sensor

class FluxCore:
    """
    A fundamental unit of existence whose physics are governed by E-M theory.
    """
    def __init__(self, size=128):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.float32)
        
        # --- E-M Sextet Properties ---
        # These now represent aeronautical concepts instead of abstract physics.
        self.specific_energy = 100.0 # (Es) Represents total state (h + V^2/2g)
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
        """
        Uses the ferro_sensor to introduce non-deterministic environmental
        factors that can affect the E-M calculations (e.g., air density).
        """
        sensor_data = ferro_sensor.get_sextet()
        # Permeability now acts like air density, affecting thrust and drag.
        self.environment_factor = np.clip(sensor_data.get('permeability', 1.0), 0.5, 1.5)

    def maneuver(self, thrust_change, load_factor_change):
        """
        Represents a PERTURBO command. A maneuver changes the energy state.
        This replaces the abstract 'perturb' method.
        """
        self._sync_environmental_factors()
        
        self.thrust += thrust_change
        self.load_factor = max(1.0, self.load_factor + load_factor_change)

        # Drag increases with the square of the load factor (like in aircraft)
        self.drag = 95.0 * (self.load_factor**2) * self.environment_factor
        
        self._update_energy_state()
        self._update_memory(f"Maneuver: T={thrust_change}, n={load_factor_change}")

    def stabilize(self):
        """
        Represents a CONVERGO command. The core seeks a stable energy state.
        This replaces the abstract 'converge' method.
        """
        # Seeks equilibrium where Thrust slightly exceeds Drag
        self.thrust *= 0.95 
        self.load_factor *= 0.9
        self.load_factor = max(1.0, self.load_factor)
        
        self.drag = 95.0 * (self.load_factor**2) * self.environment_factor
        
        self._update_energy_state()
        self._update_memory("Stabilize")

    def _update_energy_state(self):
        """
        Calculates the new Specific Energy based on Specific Excess Power (Ps).
        This is the core of the E-M simulation.
        """
        # Specific Excess Power (Ps) is the rate of change of energy
        # Ps = (Thrust - Drag) * Velocity / Weight
        specific_excess_power = ((self.thrust * self.environment_factor) - self.drag) * self.velocity / self.weight
        
        # Update the core's total energy state
        self.specific_energy += specific_excess_power
        
        # Velocity is a function of the current energy state
        self.velocity = np.sqrt(max(0, self.specific_energy)) * 0.1
        
        # Update the visual grid to represent the energy state
        # High energy = bright center, low energy = dim
        center_brightness = np.clip(self.specific_energy / 200.0, 0, 1)
        self.grid = np.zeros((self.size, self.size), dtype=np.float32)
        cv2.circle(self.grid, (self.size//2, self.size//2), int(self.size/4), center_brightness, -1)

    def _update_memory(self, change):
        """Records a change to the core's short-term memory."""
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100: self.memory_patterns.pop(0)

    def display(self):
        """Returns a string representation of the core's E-M state."""
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"SPECIFIC ENERGY (Es): {self.specific_energy:.2f}\n"
                f"E-M SEXTET: T={self.thrust:.2f}, D={self.drag:.2f}, V={self.velocity:.2f}, W={self.weight:.2f}, n={self.load_factor:.2f}\n"
                f"CONTEXTUS:\n{context_str}")

class Intellectus(FluxCore):
    """A specialized E-M core with enhanced learning/adaptation."""
    def __init__(self, architecture='TRANSFORMER', size=128):
        super().__init__(size)
        self.architecture = architecture
        # More efficient "engine"
        if self.architecture == 'TRANSFORMER':
            self.weight = 8.0 # Lighter, more agile

    def maneuver(self, thrust_change, load_factor_change):
        # Transformer architecture is more efficient with thrust
        super().maneuver(thrust_change * 1.2, load_factor_change)
