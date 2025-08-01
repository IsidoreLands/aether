#!/usr/bin/env python3

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
        raise NotImplementedError("Query method must be implemented by a subclass.")

# --- Google Gemini API Oracle ---

class GeminiOracle(Oracle):
    """An oracle that connects to the Google Gemini API."""
    def __init__(self, model_name):
        super().__init__(model_name)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        if not self.api_key:
            print("WARN: GEMINI_API_KEY not found. Falling back to Ollama if available.")
        
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
            # Check if Ollama is running
            response = requests.get(self.endpoint.rsplit('/', 1)[0] + '/tags', timeout=5)
            if response.status_code != 200:
                return "ORACULUM ERRORUM: Ollama not running or inaccessible."
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
        oracle = GeminiOracle(model_name)
        # Fallback to Ollama if Gemini key is missing
        if not oracle.api_key:
            return OllamaOracle(model_name)
        return oracle
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