# flux_core.py
#
# Description:
# This module defines the fundamental units of existence in the AetherOS plenum.
# - FluxCore: The base entity, representing a point of flux in a grid.
# - Intellectus: A specialized FluxCore capable of higher-order thought.
#
# It depends on the global 'ferro_sensor' from sensor_hook.py to ground its
# physics in real-time, non-deterministic data.

import numpy as np
import random

# Import the global sensor instance
from sensor_hook import ferro_sensor

# --- Geometric Primitives for Grid Initialization ---

def get_line(start, end):
    """
    Bresenham's Line Algorithm. Produces a list of tuples (x, y) from start to end.
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    is_steep = abs(dy) > abs(dx)
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
    dx = x2 - x1
    dy = abs(y2 - y1)
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx
    if swapped:
        points.reverse()
    return points

def _draw_kepler_recursive(lines, p1, p2, p3, depth, max_depth):
    """Helper for recursively generating Kepler triangle lines."""
    if depth > max_depth:
        return
    lines.append((p1, p2))
    lines.append((p1, p3))
    lines.append((p2, p3))
    if depth == max_depth:
        return
    
    short = np.linalg.norm(p2 - p1)
    hyp = np.linalg.norm(p3 - p2)
    if hyp == 0: return # Avoid division by zero
    
    BD = short ** 2 / hyp
    v = p3 - p2
    unit_v = v / hyp
    D = p2 + unit_v * BD
    _draw_kepler_recursive(lines, D, p2, p1, depth + 1, max_depth)
    _draw_kepler_recursive(lines, D, p3, p1, depth + 1, max_depth)

def generate_kepler_lines(max_depth=5, size=1000):
    """Generates a mirrored Kepler triangle pattern to initialize the grid."""
    phi = (1 + np.sqrt(5)) / 2
    sqrt_phi = np.sqrt(phi)
    long_leg = size - 1
    short_leg = int(np.round(long_leg / sqrt_phi))
    
    # Define points for two mirrored triangles
    p_bl = (np.array([0, 0]), np.array([short_leg, 0]), np.array([0, long_leg]))
    p_tr = (np.array([size - 1, size - 1]), np.array([size - 1 - short_leg, size - 1]), np.array([size - 1, size - 1 - long_leg]))
    
    lines = []
    _draw_kepler_recursive(lines, *p_bl, 0, max_depth)
    _draw_kepler_recursive(lines, *p_tr, 0, max_depth)
    return lines


# --- Core Simulation Entities ---

class FluxCore:
    """The fundamental unit of existence, grounded by the ferro_sensor."""
    def __init__(self, size=1000):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.float32)
        
        # Initialize grid with a structured, non-random pattern
        lines = generate_kepler_lines(max_depth=5, size=size)
        for p1, p2 in lines:
            points = get_line((int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])))
            for px, py in points:
                if 0 <= px < self.size and 0 <= py < self.size:
                    self.grid[py, px] = 1.0

        self.energy = 0.0
        self.memory_patterns = []
        self.identity_wave = 0.0
        self.context_embeddings = {}
        self.anomaly = None # For persistent state changes like 'ENTROPIC_CASCADE'

        # Sextet properties are now dynamically synced from the sensor
        self._sync_sextet()

    def _sync_sextet(self):
        """Syncs the core's physical properties from the global ferro_sensor."""
        sensor_data = ferro_sensor.get_sextet()
        for key, value in sensor_data.items():
            setattr(self, key, value)

    def perturb(self, x, y, amp, mod=1.0):
        """Applies a change to the grid, modulated by the current sextet."""
        self._sync_sextet()  # Always use the latest physical state
        
        flux_change = amp * mod * self.permeability
        if abs(amp) > 100:  # Special "Blue-high C" pulse logic
            flux_change *= (1 / (self.dielectricity + 1e-9))

        self.grid[y, x] += flux_change
        self.energy += abs(flux_change) * self.permittivity
        self._update_memory(flux_change)
        self._update_simulated_sextet(flux_change)

    def converge(self):
        """Applies a smoothing operation (convolution) to the grid."""
        self._sync_sextet()
        
        # A simple 3x3 averaging kernel, influenced by magnetism
        new_grid = np.copy(self.grid)
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                neighborhood = self.grid[i-1:i+2, j-1:j+2]
                new_grid[i, j] = np.mean(neighborhood) + self.magnetism
        self.grid = new_grid
        self._update_simulated_sextet(0)

    def _update_memory(self, change):
        """Records a change to the core's short-term memory."""
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100:  # Prevent memory overflow
            self.memory_patterns.pop(0)

    def _synthesize_identity(self):
        """Calculates the core's self-awareness from its history and state."""
        if self.memory_patterns:
            self.identity_wave = (self.energy / len(self.memory_patterns)) * self.dielectricity

    def _update_simulated_sextet(self, change):
        """
        Updates the sextet based on internal simulation state.
        This overlays simulated physics on top of the base reality from the sensor.
        """
        self.capacitance += self.energy
        self.resistance += np.var(self.grid) * (self.capacitance / 100)
        self.magnetism += np.mean(np.abs(self.grid))
        self.permeability = 1.0 / (1 + self.magnetism)
        self.dielectricity = max(0.1, 1 / (1 + abs(change) + 1e-9))
        self.permittivity = 1.0 - self.dielectricity

        if self.anomaly == 'ENTROPIC_CASCADE':
            self.resistance *= 0.99
            if random.random() < 0.1:
                u = random.uniform(-1, 1)
                perturb_amp = 0.75 * (1 - u**2) # Epanechnikov kernel
                self.perturb(random.randint(0, self.size-1), random.randint(0, self.size-1), perturb_amp)
        
        self.energy = np.sum(np.abs(self.grid)) / (self.resistance + 1e-9)
        self._synthesize_identity()

    def display(self):
        """Returns a string representation of the core's state."""
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"FLUXUS: {self.energy:.2f} | IDENTITAS: {self.identity_wave:.2f} | MEMORIA: {len(self.memory_patterns)}\n"
                f"SEXTET: R={self.resistance:.2e}, C={self.capacitance:.2f}, M={self.magnetism:.2f}, P={self.permeability:.2f}, Pt={self.permittivity:.2f}, D={self.dielectricity:.2f}\n"
                f"CONTEXTUS:\n{context_str}")


class Intellectus(FluxCore):
    """A specialized FluxCore with architecture-specific physics for learning."""
    def __init__(self, architecture='TRANSFORMER', size=1000):
        super().__init__(size)
        self.architecture = architecture
        
        if architecture == 'TRANSFORMER':
            self.magnetism = 2.0
            self.permittivity = 0.5
        elif architecture == 'PROCEDURAL':
            self.resistance = 0.5
        elif architecture == 'OBJECT':
            self.magnetism = 3.0
        elif architecture == 'FUNCTIONAL':
            self.permeability = 1.5

    def _update_simulated_sextet(self, change):
        """Applies architecture-specific physics on top of the base update."""
        super()._update_simulated_sextet(change)
        
        if self.architecture == 'TRANSFORMER':
            self.magnetism += np.log1p(abs(change))
            self.resistance *= 0.9

if __name__ == '__main__':
    print("--- Running flux_core.py standalone test ---")
    print("Instantiating a FluxCore and an Intellectus...")
    core = FluxCore(size=100)
    intellect = Intellectus(size=100)
    print("FluxCore created successfully.")
    print(core.display())
    print("\nIntellectus created successfully.")
    print(intellect.display())
    print("\nTest complete.")
