# experiri/model_loader.py (Final Version)
import json
import os
import numpy as np

# Import ALL player classes, including the new HuggingFacePlayer
from experiri.players import (
    HRMPlayer,
    SemanticHRMPlayer,
    ARCPlayer,
    OllamaPlayer,
    HuggingFacePlayer 
)

SYSTEM_STATUS_PATH = "/tmp/sm_status.json"
MODEL_CHARS_PATH = "registry/model_characteristics.json"
# Add the new player to the class registry
PLAYER_CLASSES = {
    "HRMPlayer": HRMPlayer,
    "SemanticHRMPlayer": SemanticHRMPlayer,
    "ARCPlayer": ARCPlayer,
    "OllamaPlayer": OllamaPlayer,
    "HuggingFacePlayer": HuggingFacePlayer
}

def get_system_state():
    # ... (function is unchanged) ...
    if not os.path.exists(SYSTEM_STATUS_PATH): return 100
    try:
        with open(SYSTEM_STATUS_PATH, 'r') as f: data = json.load(f)
        return int(data.get("current", 100))
    except (json.JSONDecodeError, ValueError): return 100

def get_model_characteristics():
    # ... (function is unchanged) ...
    if not os.path.exists(MODEL_CHARS_PATH): raise FileNotFoundError(f"Chars file not found at: {MODEL_CHARS_PATH}")
    with open(MODEL_CHARS_PATH, 'r') as f: return json.load(f)

def load_player(model_key: str):
    # ... (core load_player logic is unchanged) ...
    system_sm = get_system_state()
    all_model_chars = get_model_characteristics()
    model_chars = all_model_chars.get(model_key)
    if not model_chars: raise ValueError(f"Model key '{model_key}' not found in model_characteristics.json")
    
    params = model_chars.get("parameters_billions", 1.0)
    tps = model_chars.get("tokens_per_second_on_roma", 30.0)
    demand_score = (params * 20) / (np.sqrt(tps) + 0.5)
    print(f"< System Maneuverability: {system_sm} | Model '{model_key}' Demand: {demand_score:.2f} >")
    
    if demand_score > system_sm: raise PermissionError(f"Insufficient SM ({system_sm}) to manifest '{model_key}' (Demand: {demand_score:.2f}).")
    
    with open('registry/model_registry.json', 'r') as f: registry = json.load(f)
    config = registry.get(model_key)
    if not config: raise ValueError(f"Model key '{model_key}' not found in model_registry.json")
    
    PlayerClass = PLAYER_CLASSES[config['class']]
    print(f"< Decision: Manifesting '{model_key}'. Virtuous service is possible. >")
    return PlayerClass(config)
