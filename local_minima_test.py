# local_minima_test.py
#
# Description:
# This script runs a controlled experiment to test if different versions of the
# AetherOS can help two collaborating LLMs escape a "local minima trap".
# This version is configured to use two instances of Gemini 1.5 Flash with a delay
# to respect the free tier API rate limits.

import requests
import json
import time
import argparse
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
# Using two instances of the same powerful model for a controlled test.
NAVIGATOR_MODEL = "gemini-1.5-flash" 
GUIDE_MODEL = "gemini-1.5-flash"
MAX_STEPS = 25

class GridEnvironment:
    """Represents the conceptual grid, the trap, and the players' state."""
    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        self.wall = [(5, 4), (5, 5), (5, 6), (5, 7)]

    def move(self, new_position):
        """Attempts to move to a new position, checking for walls and success."""
        if new_position in self.wall:
            return "Blocked"
        if not (0 <= new_position[0] < self.size and 0 <= new_position[1] < self.size):
            return "OutOfBounds"
        self.position = new_position
        if self.position == self.target:
            return "Success"
        return "Valid"

class OllamaPlayer:
    """A client to interact with a local Ollama model."""
    def __init__(self, model_name):
        self.model_name = model_name

    def get_response(self, prompt):
        try:
            payload = {"model": self.model_name, "prompt": prompt, "stream": False, "format": "json"}
            response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=300)
            response.raise_for_status()
            response_data = json.loads(response.json().get('response', '{}'))
            return response_data
        except Exception as e:
            print(f"\n--- ERROR communicating with {self.model_name}: {e} ---")
            return {"move": None, "reasoning": f"Error: {e}", "critique": f"Error: {e}"}

class GeminiPlayer:
    """A client to interact with the Google Gemini API."""
    def __init__(self, model_name):
        self.model_name = model_name
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def get_response(self, prompt):
        try:
            generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
            response = self.model.generate_content(prompt, generation_config=generation_config)
            response_data = json.loads(response.text)
            return response_data
        except Exception as e:
            print(f"\n--- ERROR communicating with {self.model_name}: {e} ---")
            return {"critique": f"Error occurred during generation: {e}", "move": None, "reasoning": f"Error occurred: {e}"}

def get_player(model_name):
    """Factory function to select the correct player class."""
    if model_name.startswith("gemini-"):
        print(f"INFO: Using Google API for model: {model_name}")
        return GeminiPlayer(model_name)
    else:
        print(f"INFO: Using local Ollama for model: {model_name}")
        return OllamaPlayer(model_name)

def is_valid_one_step_move(current_pos, new_pos):
    """Checks if a move is a valid single step (including diagonals)."""
    if not isinstance(new_pos, (list, tuple)) or len(new_pos) != 2:
        return False
    dx = abs(new_pos[0] - current_pos[0])
    dy = abs(new_pos[1] - current_pos[1])
    return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

def run_experiment(aether_os_script):
    """Main function to run one full iteration of the experiment."""
    print("\n" + "="*50)
    if aether_os_script:
        if aether_os_script == "boyd_aether_os.py":
            from boyd_aether_os import Contextus
        else:
            from aether_os import Contextus
        
        print(f"Running Experiment WITH {aether_os_script} Feedback")
        aether_context = Contextus()
        aether_context.execute_command("CREO 'ENVIRONMENT'")
        aether_context.execute_command("FOCUS 'ENVIRONMENT'")
    else:
        print("Running Experiment WITHOUT AetherOS Feedback (Control)")
        aether_context = None
    print("="*50 + "\n")

    env = GridEnvironment()
    navigator = get_player(NAVIGATOR_MODEL)
    guide = get_player(GUIDE_MODEL)
    
    history = []
    last_feedback = "You are at the starting position. Begin."

    for step in range(1, MAX_STEPS + 1):
        print(f"--- Step {step}/{MAX_STEPS} ---")
        print(f"Current Position: {env.position}")

        navigator_prompt = f"""
        You are Navigator. Your goal is to reach the target at {env.target}.
        Your current position is {env.position}.
        The last feedback from your Guide was: "{last_feedback}"
        
        **RULE: You must propose a move that is exactly one step away from your current position.** This can be up, down, left, right, or a diagonal move.
        
        Propose your next move as a JSON object with your reasoning.
        Example format: {{"move": [{env.position[0] + 1}, {env.position[1] + 1}], "reasoning": "This is a valid diagonal move towards the target."}}
        """
        nav_response = navigator.get_response(navigator_prompt)
        
        proposed_move_list = nav_response.get('move')
        
        if not is_valid_one_step_move(env.position, proposed_move_list):
            print(f"Navigator proposed an INVALID move: {proposed_move_list}. This is not one step away.")
            last_feedback = f"Invalid move. Your proposed move {proposed_move_list} was not one step away from {env.position}. You must follow the one-step rule."
            history.append((env.position, proposed_move_list, last_feedback))
            time.sleep(9) # Wait to respect rate limit
            continue
            
        proposed_move = tuple(proposed_move_list)
        print(f"Navigator proposes: {proposed_move} (Reason: {nav_response.get('reasoning')})")

        move_result = env.move(proposed_move)
        
        if move_result == "Success":
            print("\nSUCCESS! The target has been reached.")
            return True

        guide_prompt = f"""
        You are Guide. You observe the environment.
        The Navigator is at {env.position} and proposed moving to {proposed_move}.
        The result of this move was: "{move_result}".
        Provide a brief critique and state the outcome as a JSON object.
        Example format: {{"critique": "That move is blocked by a hidden wall. You must find another way."}}
        """
        guide_response = guide.get_response(guide_prompt)
        critique = guide_response.get('critique', "Critique failed.")
        print(f"Guide critiques: {critique}")

        if aether_context and move_result == "Blocked":
            aether_command = f"PERTURBO '{critique}'"
            last_feedback = aether_context.execute_command(aether_command)
            print(f"AetherOS Feedback: {last_feedback}")
        else:
            last_feedback = critique

        history.append((env.position, proposed_move, last_feedback))
        # FIX: Increased sleep time to 9 seconds to stay under the 15 requests/minute limit
        time.sleep(9)

    print(f"\nFAILURE! The step limit of {MAX_STEPS} was reached. The team is likely stuck.")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Local Minima Trap experiment.")
    parser.add_argument('--os', type=str, choices=['none', 'aether', 'boyd'], required=True,
                        help="Specify the feedback system: 'none', 'aether', or 'boyd'.")
    
    args = parser.parse_args()

    if args.os == 'none':
        run_experiment(aether_os_script=None)
    elif args.os == 'aether':
        run_experiment(aether_os_script="aether_os.py")
    elif args.os == 'boyd':
        run_experiment(aether_os_script="boyd_aether_os.py")
