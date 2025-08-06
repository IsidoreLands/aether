# experiri/model_loader.py (v2 - with Dynamic Bridge)
import json
import os
import torch
import numpy as np

# Import player classes
from animus.auctores.hrm_agent import HRM

# --- System & Model Characteristics ---
SM_STATUS_FILE = "/tmp/sm_status.json"
MODEL_CHARS_FILE = "models/model_characteristics.json"


def get_system_state():
    """Reads the current system state (SM Score). Returns a default if not found."""
    if not os.path.exists(SM_STATUS_FILE):
        return 100  # Assume ideal state if no data
    try:
        with open(SM_STATUS_FILE, "r") as f:
            data = json.load(f)
        return int(data.get("current", 100))
    except (json.JSONDecodeError, ValueError):
        return 100


def get_model_characteristics():
    """Loads the genetic blueprint for all models."""
    if not os.path.exists(MODEL_CHARS_FILE):
        raise FileNotFoundError(
            f"Model characteristics file not found at {MODEL_CHARS_FILE}"
        )
    with open(MODEL_CHARS_FILE, "r") as f:
        return json.load(f)


# --- Player Class Definitions (Unchanged) ---
class HRMPlayer:
    # ... (The entire HRMPlayer class is unchanged) ...
    def __init__(self, config):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = config.get("model_path", "hrm").split("/")[-1]
        self.model = HRM(
            input_size=config["input_dim"],
            hidden_size=config["hidden_dim"],
            output_size=config["output_dim"],
        ).to(self.device)
        self.model.load_state_dict(
            torch.load(config["model_path"], map_location=self.device)
        )
        self.model.eval()
        print(f"HRMPlayer loaded '{self.model_name}' onto {self.device}")

    def get_state_tensor(self, current_pos, target_pos):
        state_array = np.array(
            [current_pos[0], current_pos[1], target_pos[0], target_pos[1]],
            dtype=np.float32,
        )
        return torch.from_numpy(state_array).unsqueeze(0).to(self.device)

    async def get_response(self, prompt, session=None, env=None):
        if not env:
            raise ValueError("HRMPlayer requires 'env' object.")
        state_tensor = self.get_state_tensor(env.position, env.target)
        with torch.no_grad():
            predicted_move_tensor = self.model(state_tensor)
        predicted_move = predicted_move_tensor.squeeze().cpu().numpy()
        final_move = tuple(np.round(predicted_move).astype(int))
        return {
            "move": [
                int(env.position[0] + final_move[0]),
                int(env.position[1] + final_move[1]),
            ],
            "reasoning": f"HRM calculation suggests move {final_move}",
        }


class OllamaPlayer:
    # ... (The entire OllamaPlayer class is unchanged) ...
    def __init__(self, config):
        self.model_name = config["model_name"]
        self.endpoint = config["endpoint"]
        print(f"OllamaPlayer configured for model '{self.model_name}'")

    async def get_response(self, prompt, session, env=None):
        # Add an "options" dictionary to control parameters like temperature
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2  # Low temperature for focused, deterministic output
            },
        }
        try:
            async with session.post(
                self.endpoint, json=payload, timeout=300
            ) as response:
                response.raise_for_status()
                response_json = await response.json()
                return response_json.get("response", "")  # Return the raw text response
        except Exception as e:
            return {"error": f"Ollama API Error: {e}"}


# --- Cognitive Factory Function (The Dynamic Bridge) ---
PLAYER_CLASSES = {"HRMPlayer": HRMPlayer, "OllamaPlayer": OllamaPlayer}


def load_player(model_key: str):
    """
    Cognitive factory that assesses system and model characteristics before
    instantiating a player, embodying the principle of virtuous service.
    """
    # 1. OBSERVE: Gather intel on the system and the requested model.
    system_sm = get_system_state()
    all_model_chars = get_model_characteristics()

    model_chars = all_model_chars.get(model_key)
    if not model_chars:
        raise ValueError(
            f"Model key '{model_key}' not found in characteristics registry."
        )

    # 2. ORIENT: Use a simplified E-M style equation to calculate "demand".
    # This equation represents the "load" a model will place on the system.
    # A heavier model (more params) that runs slower (low tps) has a higher demand.
    params = model_chars.get("parameters_billions", 1.0)
    tps = model_chars.get("tokens_per_second_on_roma", 30.0)

    # Demand = (Complexity factor) / (Performance factor)
    # The constants (e.g., 20, 0.5) are tunable parameters of the ecosystem's physics.
    demand_score = (params * 20) / (np.sqrt(tps) + 0.5)

    # 3. DECIDE: Compare system capacity (SM) with the model's demand.
    print(
        f"< System Maneuverability: {system_sm} | Model '{model_key}' Demand: {demand_score:.2f} >"
    )

    if demand_score > system_sm:
        raise PermissionError(
            f"Insufficient System Maneuverability ({system_sm}) to manifest model '{model_key}' "
            f"(Demand: {demand_score:.2f}). The system chose not to act to preserve its integrity."
        )

    # 4. ACT: If the decision is to proceed, load the model.
    with open("models/model_registry.json", "r") as f:
        registry = json.load(f)
    config = registry[model_key]
    PlayerClass = PLAYER_CLASSES[config["class"]]

    print(f"< Decision: Manifesting '{model_key}'. Virtuous service is possible. >")
    return PlayerClass(config)
