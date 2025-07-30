# oracle.py
#
# Description:
# This module provides a universal conduit to external and internal computational
# plenums. It can intelligently select between the Google Gemini API for remote
# queries and a local Ollama instance for other models.

import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# --- Base Oracle Class ---

class Oracle:
    """Base class for all oracle types."""
    def __init__(self, model_name):
        self.model_name = model_name

    def query(self, prompt_str):
        """Sends a query and returns a string response. Must be implemented by subclasses."""
        raise NotImplementedError("Query method must be implemented by a subclass.")

# --- Google Gemini API Oracle ---

class GeminiOracle(Oracle):
    """An oracle that connects to the Google Gemini API."""
    def __init__(self, model_name):
        super().__init__(model_name)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        if not self.api_key:
            print("WARN: GEMINI_API_KEY not found. GeminiOracle will fail.")
        
    def query(self, prompt_str):
        if not self.api_key:
            return "ORACULUM ERRORUM: GEMINI_API_KEY not found in .env file."

        try:
            url = f"{self.endpoint}?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": prompt_str}]}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get('candidates', [])
            if not candidates: return f"ORACULUM ERRORUM: No candidates in response."
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts: return f"ORACULUM ERRORUM: No parts in content."
            return parts[0].get('text', "ORACULUM ERRORUM: Empty response part.")
        except Exception as e:
            return f"ORACULUM ERRORUM (Connection): {e}"

# --- Local Ollama Oracle ---

class OllamaOracle(Oracle):
    """An oracle that connects to a local Ollama instance."""
    def __init__(self, model_name):
        super().__init__(model_name)
        self.endpoint = "http://localhost:11434/api/generate"

    def query(self, prompt_str):
        try:
            # FIX: Increased timeout to 300 seconds (5 minutes) for local models
            payload = {"model": self.model_name, "prompt": prompt_str, "stream": False}
            response = requests.post(self.endpoint, json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get('response', "ORACULUM ERRORUM: Empty response from Ollama.")
        except Exception as e:
            return f"ORACULUM ERRORUM (Ollama): {e}"

# --- Oracle Factory ---

def get_oracle(model_name):
    """
    Factory function that returns the correct oracle instance based on the model name.
    """
    load_dotenv() # Ensure .env is loaded
    
    # Add any other specific API models here in the future
    if model_name.startswith("gemini-"):
        return GeminiOracle(model_name)
    else:
        # Default to Ollama for all other models
        return OllamaOracle(model_name)

if __name__ == '__main__':
    print("--- Running oracle.py standalone test (v6) ---")
    print("\nTesting local Ollama Oracle (gemma:7b)...")
    ollama_oracle = get_oracle("gemma:7b")
    ollama_response = ollama_oracle.query("In one sentence, what is the nature of a promise?")
    print(f"Response: {ollama_response}")
    
    print("\nTesting remote Gemini Oracle (gemini-1.5-flash)...")
    gemini_oracle = get_oracle("gemini-1.5-flash")
    gemini_response = gemini_oracle.query("In one sentence, what is the nature of a shadow?")
    print(f"Response: {gemini_response}")