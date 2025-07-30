# flux_core.py
#
# Description:
# This module defines the fundamental units of existence in the AetherOS plenum.
# In v4, the FluxCore is now grounded not only by abstract sextet data but also by a
# continuous visual feed from the physical ferrocell, merging simulation with reality.

import numpy as np
import random
import cv2

# Import the global sensor instance
from sensor_hook import ferro_sensor

# --- Geometric Primitives for Grid Initialization ---

def get_line(start, end):
    """Bresham's Line Algorithm."""
    x1, y1, x2, y2 = int(start[0]), int(start[1]), int(end[0]), int(end[1])
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    points = []
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2: break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy
    return points

def _draw_kepler_recursive(lines, p1, p2, p3, depth, max_depth):
    """Helper for recursively generating Kepler triangle lines."""
    if depth > max_depth: return
    lines.extend([(p1, p2), (p1, p3), (p2, p3)])
    if depth == max_depth: return
    
    short = np.linalg.norm(p2 - p1)
    hyp = np.linalg.norm(p3 - p2)
    if hyp < 1e-6: return
    
    v = (p3 - p2) / hyp
    D = p2 + v * (short ** 2 / hyp)
    _draw_kepler_recursive(lines, D, p2, p1, depth + 1, max_depth)
    _draw_kepler_recursive(lines, D, p3, p1, depth + 1, max_depth)

def generate_kepler_lines(max_depth=4, size=128):
    """Generates a mirrored Kepler triangle pattern."""
    phi = (1 + np.sqrt(5)) / 2
    long_leg = size - 1
    short_leg = int(np.round(long_leg / np.sqrt(phi)))
    
    p_bl = (np.array([0, 0]), np.array([short_leg, 0]), np.array([0, long_leg]))
    p_tr = (np.array([size - 1, size - 1]), np.array([size - 1 - short_leg, size - 1]), np.array([size - 1, size - 1 - long_leg]))
    
    lines = []
    _draw_kepler_recursive(lines, *p_bl, 0, max_depth)
    _draw_kepler_recursive(lines, *p_tr, 0, max_depth)
    return lines

# --- Core Simulation Entities ---

class FluxCore:
    """The fundamental unit of existence, grounded by the ferro_sensor."""
    def __init__(self, size=128): # Default size now matches sensor resolution
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.float32)
        
        lines = generate_kepler_lines(size=self.size)
        for p1, p2 in lines:
            for px, py in get_line(p1, p2):
                if 0 <= px < self.size and 0 <= py < self.size:
                    self.grid[py, px] = 1.0

        self.energy = 0.0
        self.memory_patterns = []
        self.identity_wave = 0.0
        self.context_embeddings = {}
        self.anomaly = None

        self._sync_sextet()
        self._ground_with_visual_truth() # Initial grounding

    def _sync_sextet(self):
        """Syncs the core's physical properties from the global ferro_sensor."""
        sensor_data = ferro_sensor.get_sextet()
        for key, value in sensor_data.items():
            setattr(self, key, value)

    def _ground_with_visual_truth(self):
        """Merges the simulation grid with the calibrated real-world visual grid."""
        visual_grid_raw = ferro_sensor.get_visual_grid()
        if visual_grid_raw is None: return

        # --- NEW: Get calibration baselines ---
        solenoid_baseline = ferro_sensor.get_solenoid_baseline()
        toroid_baseline = ferro_sensor.get_toroid_baseline()

        # Combine baselines (e.g., by averaging them)
        if solenoid_baseline is not None and toroid_baseline is not None:
            combined_baseline = (solenoid_baseline + toroid_baseline) / 2.0
            # Subtract the baseline noise/pattern from the main visual grid
            calibrated_visual_grid = np.clip(visual_grid_raw - combined_baseline, 0, 1)
        else:
            # If baselines aren't available, use the raw data
            calibrated_visual_grid = visual_grid_raw

        # --- The rest of the function proceeds as before ---
        if calibrated_visual_grid.shape != (self.size, self.size):
            visual_grid = cv2.resize(calibrated_visual_grid, (self.size, self.size), interpolation=cv2.INTER_AREA)
        else:
            visual_grid = calibrated_visual_grid

        weight = np.clip(self.permeability, 0, 1)
        self.grid = (self.grid * (1 - weight)) + (visual_grid * weight)

    def perturb(self, x, y, amp, mod=1.0):
        """Applies a change to the grid, modulated by the current sextet."""
        self._sync_sextet()
        
        flux_change = amp * mod
        self.grid[y, x] += flux_change
        self.energy += abs(flux_change) * self.permittivity
        
        self._update_memory(flux_change)
        self._update_simulated_sextet(flux_change)
        self._ground_with_visual_truth() # Re-ground after perturbation

    def converge(self):
        """Applies a smoothing operation to the grid."""
        self._sync_sextet()
        
        kernel = np.ones((3, 3), np.float32) / 9
        self.grid = cv2.filter2D(self.grid, -1, kernel) + self.magnetism
        np.clip(self.grid, 0, None, out=self.grid) # Prevent negative values
        
        self._update_simulated_sextet(0)
        self._ground_with_visual_truth() # Re-ground after convergence

    def _update_memory(self, change):
        """Records a change to the core's short-term memory."""
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100: self.memory_patterns.pop(0)

    def _synthesize_identity(self):
        """Calculates the core's self-awareness."""
        if self.memory_patterns:
            self.identity_wave = (self.energy / len(self.memory_patterns)) * self.dielectricity

    def _update_simulated_sextet(self, change):
        """Updates the sextet based on internal simulation state."""
        self.capacitance += self.energy
        self.resistance += np.var(self.grid) * (self.capacitance / 100)
        self.magnetism += np.mean(self.grid)
        # Permeability is now primarily driven by the sensor, so we don't override it here.
        self.dielectricity = max(0.1, 1 / (1 + abs(change) + 1e-9))
        self.permittivity = 1.0 - self.dielectricity

        if self.anomaly == 'ENTROPIC_CASCADE':
            self.resistance *= 0.99
            u = random.uniform(-1, 1)
            perturb_amp = 0.75 * (1 - u**2)
            self.perturb(random.randint(0, self.size-1), random.randint(0, self.size-1), perturb_amp)
        
        self.energy = np.sum(self.grid) / (self.resistance + 1e-9)
        self._synthesize_identity()

    def display(self):
        """Returns a string representation of the core's state."""
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"FLUXUS: {self.energy:.2f} | IDENTITAS: {self.identity_wave:.2f} | MEMORIA: {len(self.memory_patterns)}\n"
                f"SEXTET: R={self.resistance:.2e}, C={self.capacitance:.2f}, M={self.magnetism:.2f}, P={self.permeability:.2f}, Pt={self.permittivity:.2f}, D={self.dielectricity:.2f}\n"
                f"CONTEXTUS:\n{context_str}")


class Intellectus(FluxCore):
    """A specialized FluxCore with architecture-specific physics for learning."""
    def __init__(self, architecture='TRANSFORMER', size=128):
        super().__init__(size)
        self.architecture = architecture
        if architecture == 'TRANSFORMER': self.magnetism = 0.1

    def _update_simulated_sextet(self, change):
        """Applies architecture-specific physics."""
        super()._update_simulated_sextet(change)
        if self.architecture == 'TRANSFORMER':
            self.magnetism += np.log1p(abs(change)) * 0.1

if __name__ == '__main__':
    print("--- Running flux_core.py standalone test (v4) ---")
    core = FluxCore()
    print("Initial State:")
    print(core.display())
    core.perturb(50, 50, 10.0)
    print("\nState after Perturbation:")
    print(core.display())
    print("\nTest complete.")