Aether Model Integration Protocol

This document outlines the standardized procedure for integrating and utilizing language models within the Aether project. The system is designed to be model-agnostic, allowing for flexible experimentation with local and remote models through a centralized registry.

Core Components
Model Registry (/models/model_registry.json): A JSON file that acts as the master list of all available models. Each entry defines a model's type, its configuration, and the "Player" class responsible for interacting with it. This is the single source of truth for model definitions.
Model Loader (/experiri/model_loader.py): A Python module containing a factory function, load_player(model_key). This function reads the registry, finds the configuration for the given model_key, and returns an instantiated, ready-to-use "Player" object.
Player Classes (defined in model_loader.py): Python classes (HRMPlayer, OllamaPlayer, etc.) that implement the logic for interacting with a specific type of model (e.g., a local PyTorch model, an Ollama API endpoint). Each Player class must have a consistent get_response() method.
Local Models Directory (/models/): This directory is ignored by Git and houses local model files, such as PyTorch checkpoints (.pth). This keeps the repository lightweight.

How to Add and Use a New Model
Step 1: Place or Install the Model
For Local Checkpoints (e.g., HRM): Place the .pth file inside /models/hrm_checkpoints/.
For System-Wide Ollama Models: Install the model using the command line: ollama pull <model_name>.
Step 2: Register the Model
Edit /models/model_registry.json and add a new entry for the model. The entry must include:
A unique model_key (e.g., "ollama_new_model").
"type": The category of the model (e.g., "ollama", "hrm").
"class": The name of the Python Player class that handles this model type.
Any other necessary configuration parameters (model_name, endpoint, model_path, etc.).
Example Entry for a new Ollama model:
Generated json
"ollama_llama3": {
  "type": "ollama",
  "class": "OllamaPlayer",
  "model_name": "llama3",
  "endpoint": "http://localhost:11434/api/generate"
}
Use code with caution.
Json
Step 3: Use the Model in a Script
To use one or more models within any script (e.g., a test in /experiri/ or a tool in /sagas/):
Import the loader:
Generated python
from experiri.model_loader import load_player
Use code with caution.
Python
Call load_player() for each required model: Store the returned Player object in a descriptive variable. This makes handling multiple models clean and simple.
Generated python
# Load two different models for two different roles
navigator = load_player('ollama_phi3')
guide = load_player('ollama_qwen7b')
Use code with caution.
Python
Use the Player objects: Call the .get_response() method on the corresponding object.
Generated python
nav_output = await navigator.get_response(navigator_prompt, session)
guide_output = await guide.get_response(guide_prompt, session)
Use code with caution.
Python
This protocol ensures that all scripts remain model-agnostic. The script logic only needs to know the model_key; the model_loader handles all implementation details.
