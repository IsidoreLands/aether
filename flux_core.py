# flux_core.py
#
# Description:
# This module defines the fundamental units of existence in the AetherOS plenum.
# CORRECTED: FluxCore now correctly represents the 1000x1000 state grid (the Flux Grid),
# and all geometric rendering logic is correctly delegated to the remote Ferrocella server.

import numpy as np
import random
import cv2
import os

# --- Imports for the Networked Hardware Interface ---
from ferramenta.fluo.hardware_interface import RemoteFerrocell

# Get the server URL from an environment variable for flexibility.
REMOTE_FERROCELLA_URL = os.environ.get(
    "FERROCELLA_URL",
    "http://placeholder.ngrok-free.app"
)

# Initialize the global hardware client
try:
    ferro_sensor = RemoteFerrocell(remote_address=REMOTE_FERROCELLA_URL)
except RuntimeError as e:
    print(f"FATAL ERROR: Could not initialize hardware link. {e}")
    print("WARNING: AetherOS is running in a DISCONNECTED state.")
    ferro_sensor = None

# --- REMOVED: All geometric drawing functions (get_line, etc.) ---
# These functions do not belong in the "mind" (AetherOS). They are part
# of the "body" (Ferrocella) and have been correctly removed.


# --- Core Simulation Entities ---

class FluxCore:
    """
    The fundamental unit of existence, representing the state of the
    1000x1000 Flux Grid.
    """
    def __init__(self):
        # The Flux Grid is a fixed, high-resolution 1000x1000 canvas.
        self.size = 1000
        self.grid = np.zeros((self.size, self.size), dtype=np.float32)
        
        self.energy = 0.0
        self.memory_patterns = []
        self.identity_wave = 0.0
        self.context_embeddings = {}
        self.anomaly = None

        # Initialize sextet attributes with defaults
        self.resistance = 1e-9; self.capacitance = 0.0; self.permeability = 1.0
        self.magnetism = 0.0; self.permittivity = 1.0; self.dielectricity = 0.0

        # The initial state is determined by sensing the world.
        print(f"FluxCore '{id(self)}' created. Performing initial grounding...")
        self._ground_with_visual_truth()

    def _sync_sextet(self):
        """Syncs the core's physical properties from the hardware interface."""
        if not ferro_sensor: return
        sensor_data = ferro_sensor.get_sextet()
        for key, value in sensor_data.items():
            setattr(self, key, value)

    def _ground_with_visual_truth(self):
        """
        Senses the world by requesting the full 1000x1000 visual state
        from the remote Ferrocella server.
        """
        if not ferro_sensor: return

        # The 'paths' argument tells the Ferrocella server how to stimulate
        # the physics before returning the resulting state. This is how the
        # "mind" acts upon the "body".
        paths_to_ground = ["A-B", "C-E"]
        
        visual_grid_data = ferro_sensor.get_visual_grid(
            paths=paths_to_ground,
            grid_size=self.size  # Request the full 1000x1000 grid
        )
        
        # This check anticipates Phase 2, where the server will send real array data.
        if isinstance(visual_grid_data, np.ndarray):
            if visual_grid_data.shape == (self.size, self.size):
                self.grid = visual_grid_data
            else:
                # Resize if there's a mismatch, though ideally server sends correct size
                self.grid = cv2.resize(visual_grid_data, (self.size, self.size), interpolation=cv2.INTER_AREA)
        else:
            # Handle the current placeholder string from the server.
            # In a disconnected state, the grid remains zeros.
            print(f"Received placeholder grounding data: {visual_grid_data}")


    def perturb(self, x, y, amp, mod=1.0):
        """
        Applies a localized, internal change to the Flux Grid. This represents
        an abstract thought or memory recall, distinct from a physical grounding.
        """
        # Note: We do not call _sync_sextet or _ground_with_visual_truth here
        # to allow for purely internal state changes.
        flux_change = amp * mod
        # Ensure coordinates are within bounds
        if 0 <= x < self.size and 0 <= y < self.size:
            self.grid[y, x] += flux_change
        
        self._update_memory(flux_change)
        self._update_simulated_sextet(flux_change) # Update physics based on the new internal state

    def converge(self):
        """Applies a smoothing/stabilizing operation and then re-grounds with reality."""
        self._sync_sextet()
        kernel = np.ones((3, 3), np.float32) / 9
        self.grid = cv2.filter2D(self.grid, -1, kernel) + self.magnetism
        np.clip(self.grid, 0, None, out=self.grid)
        
        # After converging, sense the world again to see the result.
        self._ground_with_visual_truth()
        self._update_simulated_sextet(0)

    # --- The rest of the class methods are largely unchanged ---
    def _update_memory(self, change):
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100: self.memory_patterns.pop(0)

    def _synthesize_identity(self):
        if self.memory_patterns and len(self.memory_patterns) > 0:
            self.identity_wave = (self.energy / len(self.memory_patterns)) * self.dielectricity

    def _update_simulated_sextet(self, change):
        self.capacitance += self.energy
        self.resistance += np.var(self.grid) * (self.capacitance / 100 if self.capacitance > 0 else 1)
        self.magnetism += np.mean(self.grid)
        self.dielectricity = max(0.1, 1 / (1 + abs(change) + 1e-9))
        self.permittivity = 1.0 - self.dielectricity
        self.energy = np.sum(self.grid) / (self.resistance + 1e-9 if self.resistance > 0 else 1e-9)
        self._synthesize_identity()
        
    def display(self):
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"FLUXUS: {self.energy:.2f} | IDENTITAS: {self.identity_wave:.2f} | MEMORIA: {len(self.memory_patterns)}\n"
                f"SEXTET: R={self.resistance:.2e}, C={self.capacitance:.2f}, M={self.magnetism:.2f}, P={self.permeability:.2f}, Pt={self.permittivity:.2f}, D={self.dielectricity:.2f}\n"
                f"CONTEXTUS:\n{context_str}")


class Intellectus(FluxCore):
    """A specialized FluxCore. Its fundamental nature is also 1000x1000."""
    def __init__(self, architecture='TRANSFORMER'):
        # The size is no longer a parameter; it's a constant of the universe.
        super().__init__()
        self.architecture = architecture
        if architecture == 'TRANSFORMER': self.magnetism = 0.1

    def _update_simulated_sextet(self, change):
        super()._update_simulated_sextet(change)
        if self.architecture == 'TRANSFORMER':
            self.magnetism += np.log1p(abs(change)) * 0.1
