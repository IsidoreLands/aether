# oracle.py
#
# Description:
# This module provides a hardened conduit to external computational plenums (APIs).
# The OracleMateria class handles loading model configurations, managing API keys,
# and executing queries.

import os
import json
import requests
from dotenv import load_dotenv

class OracleMateria:
    """A conduit to an external AI model API."""
    def __init__(self, model_name, models_dir="~/isidore_models"):
        """
        Initializes the Oracle for a specific model.

        Args:
            model_name (str): The name of the model to use (e.g., 'google-gemini-1.5-flash').
            models_dir (str): The directory where model configuration files are stored.
        """
        self.model_name = model_name
        self.config = self._load_config(models_dir)
        self.api_key = None
        self.endpoint = None

        if self.config:
            api_key_env_var = self.config.get("api_key_env_var")
            self.endpoint = self.config.get("api_endpoint")

            if api_key_env_var:
                self.api_key = os.environ.get(api_key_env_var)
                if not self.api_key:
                    dotenv_path = os.path.expanduser("~/aiops_toolkit/.env")
                    if os.path.exists(dotenv_path):
                        load_dotenv(dotenv_path=dotenv_path)
                        self.api_key = os.environ.get(api_key_env_var)

    def _load_config(self, models_dir):
        """Loads the JSON configuration for the specified model."""
        try:
            config_path = os.path.expanduser(os.path.join(models_dir, self.model_name, "config.json"))
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # This is an expected case if configs aren't set up, so no print needed.
            return None
        except Exception as e:
            print(f"CONFIG ERROR: Could not load config for '{self.model_name}': {e}")
            return None

    def query(self, prompt_str):
        """
        Sends a query to the external oracle via the configured API.

        Args:
            prompt_str (str): The prompt to send to the model.

        Returns:
            str: The text response from the model or an error message.
        """
        if not self.config:
            return "ORACULUM ERRORUM: Model configuration not found."
        if not self.api_key:
            api_key_name = self.config.get("api_key_env_var", "UNKNOWN_KEY")
            return f"ORACULUM ERRORUM: API key '{api_key_name}' not found."
        if not self.endpoint:
            return "ORACULUM ERRORUM: API endpoint not found in config."

        try:
            url = f"{self.endpoint}?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": prompt_str}]}]}
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            
            data = response.json()
            
            # Safer response parsing
            candidates = data.get('candidates', [])
            if not candidates:
                return f"ORACULUM ERRORUM: No candidates in response. Full response: {data}"
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                return f"ORACULUM ERRORUM: No parts in content. Full content: {content}"
                
            return parts[0].get('text', "ORACULUM ERRORUM: Empty response part.")

        except requests.exceptions.RequestException as e:
            return f"ORACULUM ERRORUM (Connection): {e}"
        except Exception as e:
            return f"ORACULUM ERRORUM (Execution): {e}"

if __name__ == '__main__':
    print("--- Running oracle.py standalone test ---")
    print("This test requires a valid '~/isidore_models/google-gemini-1.5-flash/config.json' and API key.")
    
    # Create a dummy config and .env for testing if they don't exist
    models_path = os.path.expanduser('~/isidore_models/google-gemini-1.5-flash')
    if not os.path.exists(models_path):
        os.makedirs(models_path)
    
    dummy_config_path = os.path.join(models_path, 'config.json')
    if not os.path.exists(dummy_config_path):
        print("Creating dummy config for test...")
        with open(dummy_config_path, 'w') as f:
            json.dump({
                "api_key_env_var": "TEST_API_KEY",
                "api_endpoint": "https://example.com/api"
            }, f)
            
    # Set a dummy key if not present
    if "TEST_API_KEY" not in os.environ:
        print("Setting dummy API key for test...")
        os.environ["TEST_API_KEY"] = "dummy_key_for_testing_only"

    oracle = OracleMateria('google-gemini-1.5-flash')
    print(f"Attempting query (this will fail without a real endpoint)...")
    response = oracle.query("What is the nature of flux?")
    print(f"Response: {response}")
    print("\nTest complete.")
