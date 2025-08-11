# ferramenta/fluo/hardware_interface.py
# The Hardware Abstraction Layer for AetherOS.
# This version acts as a pure network client, connecting to a remote
# Ferrocella simulation server.

import requests
import numpy as np
import base64
import zlib
import warnings

# We create a global session object for performance. This reuses the
# underlying TCP connection for multiple requests to the same server.
SESSION = requests.Session()

class RemoteFerrocell:
    """
    A client that connects to a remote Ferrocella physics server.
    This class is the bridge between the AetherOS "brain" and the
    simulated or physical "body".
    """

    def __init__(self, remote_address):
        # Ensure the address doesn't have a trailing slash
        self.base_url = remote_address.rstrip('/')
        self.api_field_url = f"{self.base_url}/api/field"
        
        print(f"INFO: Hardware interface pointing to remote server: {self.base_url}")
        
        try:
            # Test connection on startup by making a simple OPTIONS request
            response = SESSION.options(self.base_url, timeout=10)
            response.raise_for_status()
            print("INFO: Successfully connected to remote Ferrocella server.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Could not connect to Ferrocella server at {self.base_url}. Is it running? Error: {e}")

    def _decode_grid(self, data):
        """Decodes a grid received from the server."""
        if not data or 'image_png_base64' not in data:
            warnings.warn("Warning: Received a response from server with no image data.")
            return None
            
        img_b64 = data['image_png_base64']
        # This part is a placeholder for now. Decoding a PNG to a NumPy array
        # requires an image library like Pillow or OpenCV. We'll add that
        # dependency later. For now, we know the communication works.
        # For AI training, the server should ideally send the raw NumPy array
        # directly, not a PNG. We can upgrade the server to do this in Phase 2.
        return f"Received image data of length {len(img_b64)}"

    def get_sextet(self):
        """
        Placeholder. In Phase 2, the server will have a '/api/sextet'
        endpoint that returns the live physical properties.
        """
        # For now, return a default "neutral" state.
        return {
            'resistance': 1.0, 'capacitance': 1.0, 'permeability': 1.0,
            'magnetism': 0.0, 'permittivity': 1.0, 'dielectricity': 0.0
        }

    def get_visual_grid(self, paths, grid_size=200):
        """
        Requests a visual grid from the server by sending a list of
        energized paths.
        """
        payload = {
            "paths": paths,
            "grid_size": grid_size
        }
        try:
            response = SESSION.post(self.api_field_url, json=payload, timeout=120)
            response.raise_for_status()
            return self._decode_grid(response.json())
        except requests.exceptions.RequestException as e:
            warnings.warn(f"Failed to get visual grid from server: {e}")
            return None

    def control_leds(self, color, brightness):
        """
        Placeholder. In Phase 2, the server will have a '/api/control/led'
        endpoint to control the lights.
        """
        print(f"SIMULATING CONTROL: Set LEDs to {color} at brightness {brightness}")
        pass # To be implemented
