# experiri/model_loader.py
import json
import os
import torch
import numpy as np

# Import the different player classes and the HRM model definition
# We use absolute paths, which our pyproject.toml setup makes possible
from animus.auctores.hrm_agent import HRM 

# --- Player Class Definitions ---
# We will define all player types here for simplicity.

class HRMPlayer:
    """A player that uses our locally trained HRM model."""
    def __init__(self, config):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = HRM(
            input_size=config['input_dim'],
            hidden_size=config['hidden_dim'],
            output_size=config['output_dim']
        ).to(self.device)
        self.model.load_state_dict(torch.load(config['model_path'], map_location=self.device))
        self.model.eval()
        print(f"HRMPlayer loaded '{config['model_path']}' onto {self.device}")

    def get_state_tensor(self, current_pos, target_pos):
        """Converts positions to a tensor for the HRM."""
        state_array = np.array([current_pos[0], current_pos[1], target_pos[0], target_pos[1]], dtype=np.float32)
        return torch.from_numpy(state_array).unsqueeze(0).to(self.device)

    async def get_response(self, prompt, session=None, env=None):
        """'Fakes' a response by running the model."""
        if not env:
            raise ValueError("HRMPlayer requires the 'env' object to get state.")
        
        state_tensor = self.get_state_tensor(env.position, env.target)
        with torch.no_grad():
            predicted_move_tensor = self.model(state_tensor)
        
        predicted_move = predicted_move_tensor.squeeze().cpu().numpy()
        final_move = tuple(np.round(predicted_move).astype(int))
        
        # The HRM can't "reason" in words, so we provide a placeholder
        return {
            "move": [int(env.position[0] + final_move[0]), int(env.position[1] + final_move[1])],
            "reasoning": f"HRM calculation from {env.position} suggests move {final_move}"
        }

class OllamaPlayer:
    """An async client for a local Ollama model."""
    def __init__(self, config):
        self.model_name = config['model_name']
        self.endpoint = config['endpoint']
        print(f"OllamaPlayer configured for model '{self.model_name}'")

    async def get_response(self, prompt, session, env=None):
        payload = {"model": self.model_name, "prompt": prompt, "stream": False, "format": "json"}
        try:
            async with session.post(self.endpoint, json=payload, timeout=300) as response:
                response.raise_for_status()
                # Ollama wraps the JSON in a string, so we need to parse twice.
                response_json = await response.json()
                inner_json_str = response_json.get('response', '{}')
                return json.loads(inner_json_str)
        except Exception as e:
            print(f"--- ERROR communicating with {self.model_name}: {e} ---")
            return {"move": None, "reasoning": f"Error: {e}"}

# ... other player classes like HuggingFacePlayer would go here ...

# --- Factory Function ---
PLAYER_CLASSES = {
    "HRMPlayer": HRMPlayer,
    "OllamaPlayer": OllamaPlayer,
    # "HuggingFacePlayer": HuggingFacePlayer
}

def load_player(model_key: str):
    """
    Loads a model configuration from the registry and returns an
    instantiated player object.
    """
    registry_path = 'models/model_registry.json'
    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Model registry not found at {registry_path}")

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    if model_key not in registry:
        raise ValueError(f"Model key '{model_key}' not found in registry.")

    config = registry[model_key]
    player_class_name = config['class']
    
    if player_class_name not in PLAYER_CLASSES:
        raise NotImplementedError(f"Player class '{player_class_name}' is not implemented.")
        
    PlayerClass = PLAYER_CLASSES[player_class_name]
    return PlayerClass(config)
