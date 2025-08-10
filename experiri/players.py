# experiri/players.py
# The definitive repository for all "Player" classes in the AetherOS ecosystem.

import torch
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from dotenv import load_dotenv
import logging # Add logging import
from animus.auctores.hrm_agent import HRM
import requests
import aiohttp      # <-- ADD THIS IMPORT
import asyncio      # <-- ADD THIS IMPORT FOR TIMEOUTERROR

# --- Base Player ---
class HRMPlayer:
    """The base Player for all HRM-based models."""
    def __init__(self, config):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = config.get('model_path', 'hrm').split('/')[-1]
        self.model = HRM(
            input_size=config['input_dim'],
            hidden_size=config['hidden_dim'],
            output_size=config['output_dim']
        ).to(self.device)
        self.model.load_state_dict(torch.load(config['model_path'], map_location=self.device))
        self.model.eval()
        print(f"HRMPlayer loaded '{self.model_name}' onto {self.device}")

# --- Semantic Player (Base Class for ARC) ---
class SemanticHRMPlayer(HRMPlayer):
    """The SAGA v2.0 agent that understands semantic meaning."""
    embedding_model = None
    def __init__(self, config):
        if SemanticHRMPlayer.embedding_model is None:
            model_path = 'models/all-MiniLM-L6-v2'
            print(f"INFO: Loading sentence-transformer model from local path '{model_path}'...")
            SemanticHRMPlayer.embedding_model = SentenceTransformer(model_path)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        super().__init__(config)

    def _embed_saga(self, saga_context):
        saga_text = " ".join(saga_context) if saga_context else "A new journey begins without any prior history."
        embedding = self.embedding_model.encode(saga_text, convert_to_tensor=True)
        return embedding.to(self.device)

# --- RENAMED: The final ARC Player ---
class ARCPlayer(SemanticHRMPlayer):
    """
    Animus Recurrens Cogitans (ARC). The final SAGA v3.0 agent, influenced
    by its chaotic internal 'Animus' (a FluxCore instance).
    """
    def __init__(self, config):
        # Set the final, widest input dimension before initializing
        config['input_dim'] = 10 + 384 + 6 # 10 (base) + 384 (semantic) + 6 (sextet)
        super().__init__(config)
        
    def _get_state_tensor(self, env_state):
        saga_embedding = self._embed_saga(env_state['saga_context'])
        if env_state.get('lifeline_context'):
            lifeline_embedding = self._embed_saga(env_state['lifeline_context'])
            saga_embedding = (saga_embedding + lifeline_embedding) / 2.0
            
        status_vec = [1.0, 0.0] if env_state['last_move_status'] == "Valid" else [0.0, 1.0]
        base_state_array = np.array([
            *env_state['current_pos'], *env_state['target_pos'],
            *env_state['local_walls'], *status_vec
        ], dtype=np.float32)
        base_state_tensor = torch.from_numpy(base_state_array).to(self.device)
        
        animus_sextet = env_state['animus_sextet']
        sextet_array = np.array(list(animus_sextet.values()), dtype=np.float32)
        aetheric_state_tensor = torch.from_numpy(sextet_array).to(self.device)

        full_state_tensor = torch.cat([base_state_tensor, saga_embedding, aetheric_state_tensor])
        return full_state_tensor.unsqueeze(0)

    async def get_response(self, state, session):
        state_tensor = self._get_state_tensor(state)
        with torch.no_grad():
            move_tensor = self.model(state_tensor)
        direction = tuple(np.round(move_tensor.squeeze().cpu().numpy()).astype(int))
        dx, dy = np.clip(direction[0], -1, 1), np.clip(direction[1], -1, 1)
        proposed_pos = (state['current_pos'][0] + dx, state['current_pos'][1] + dy)
        return {"move": proposed_pos}

# --- LLM Player  ---
class HuggingFacePlayer:
    """A player for interacting with the Hugging Face Inference API."""
    def __init__(self, config):
        load_dotenv() # Load the .env file if it exists
        self.model_name = config['model_name']
        self.endpoint = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.api_key = os.getenv("HF_TOKEN")
        if not self.api_key:
            # Fallback to reading the cached token file
            try:
                with open(os.path.expanduser('~/.cache/huggingface/token'), 'r') as f:
                    self.api_key = f.read().strip()
            except FileNotFoundError:
                 raise ValueError("HF_TOKEN not found in environment or cache. Please log in with 'hf auth login'.")
        print(f"HuggingFacePlayer configured for model '{self.model_name}'")

    async def get_response(self, prompt, session, env=None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {"return_full_text": False, "max_new_tokens": 250, "temperature": 0.3},
            "options": {"wait_for_model": True}
        }
        try:
            async with session.post(self.endpoint, headers=headers, json=payload, timeout=60) as response:
                response.raise_for_status()
                response_json = await response.json()
                response_text = response_json[0]['generated_text']
                
                # The response is a string containing JSON, so we must parse it
                json_start = response_text.find('[')
                if json_start == -1: json_start = response_text.find('{')
                if json_start == -1: raise ValueError("No JSON object or array found in HF response.")
                
                return json.loads(response_text[json_start:])
        except Exception as e:
            # Return a dictionary with an error key for robust error handling
            return {"error": f"Hugging Face API Error: {e}"}

# --- "Bulletproof" OllamaPlayer ---
class OllamaPlayer:
    """A more robust player for interacting with local Ollama LLMs."""
    def __init__(self, config):
        self.model_name = config['model_name']
        self.endpoint = config['endpoint']
        # Perform a quick health check on initialization
        try:
            response = requests.head(self.endpoint.replace("/api/generate", ""), timeout=5)
            response.raise_for_status()
            print(f"OllamaPlayer configured for model '{self.model_name}'. Connection successful.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama server is not reachable at {self.endpoint}. Please ensure it is running. Error: {e}")

    async def get_response(self, prompt, session, env=None):
        payload = {
            "model": self.model_name, "prompt": prompt, "stream": False,
            "format": "json", "options": {"temperature": 0.2}
        }
        logging.info(f"Sending prompt to Ollama model {self.model_name}: {prompt}")
        try:
            # Increased timeout for more patience
            async with session.post(self.endpoint, json=payload, timeout=600) as response:
                response.raise_for_status()
                response_json = await response.json()
                raw_response_content = response_json.get('response', '{}')
                logging.info(f"Received raw response from Ollama: {raw_response_content}")
                return json.loads(raw_response_content)
        except aiohttp.ClientConnectorError as e:
            logging.error(f"Ollama Connection Error: {e}")
            return {"error": f"Ollama Connection Error: Could not connect to {self.endpoint}."}
        except asyncio.TimeoutError:
            logging.error("Ollama request timed out.")
            return {"error": "Ollama request timed out after 10 minutes."}
        except Exception as e:
            logging.error(f"Ollama API Error: {e}. Raw Response: {response_json if 'response_json' in locals() else 'N/A'}")
            return {"error": f"Ollama API Error: {e}"}
