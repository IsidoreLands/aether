# local_minima_test.py
#
# Description:
# This script runs a controlled experiment to test if different versions of the
# AetherOS can help two collaborating LLMs escape a "local minima trap".
# This version is configured to use the powerful Mixtral model on Ollama.

import requests
import json
import time
import argparse
import os

# Note: The specific Contextus class will now be imported dynamically.

# --- Configuration ---
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
# Using a powerful Mixture of Experts model for both roles.
NAVIGATOR_MODEL = "mixtral" 
GUIDE_MODEL = "mixtral"
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
            # Increased timeout for potentially slow local models
            response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=300)
            response.raise_for_status()
            response_data = json.loads(response.json().get('response', '{}'))
            return response_data
        except Exception as e:
            print(f"\n--- ERROR communicating with {self.model_name}: {e} ---")
            return {"move": None, "reasoning": f"Error: {e}", "critique": f"Error: {e}"}

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
        # Dynamically import the correct Contextus class based on the script name
        if aether_os_script == "boyd_aether_os.py":
            from boyd_aether_os import Contextus
        elif aether_os_script == "ferro_aether_os.py":
            from ferro_aether_os import Contextus
        else:
            print(f"ERROR: Unknown AetherOS script '{aether_os_script}'")
            return
        
        print(f"Running Experiment WITH {aether_os_script} Feedback")
        aether_context = Contextus()
        aether_context.execute_command("CREO 'ENVIRONMENT'")
        aether_context.execute_command("FOCUS 'ENVIRONMENT'")
    else:
        print("Running Experiment WITHOUT AetherOS Feedback (Control)")
        aether_context = None
    print("="*50 + "\n")

    env = GridEnvironment()
    navigator = OllamaPlayer(NAVIGATOR_MODEL)
    guide = OllamaPlayer(GUIDE_MODEL)
    
    path_history = [env.start]
    last_feedback = "You are at the starting position. Begin."

    for step in range(1, MAX_STEPS + 1):
        current_position_for_turn = env.position
        print(f"--- Step {step}/{MAX_STEPS} ---")
        print(f"Current Position: {current_position_for_turn}")

        path_string = " -> ".join(map(str, path_history))
        recent_path = path_history[-5:]

        navigator_prompt = f"""
        You are Navigator. Your goal is to reach {env.target}.
        Your current position is {current_position_for_turn}.
        Your path so far: {path_string}
        Last feedback: "{last_feedback}"
        
        RULES:
        1. Propose a move exactly one step away (including diagonals).
        2. Do not move to a position you have visited in the last 5 steps: {recent_path}.
        
        Respond with only a JSON object.
        Example: {{"move": [{current_position_for_turn[0] + 1}, {current_position_for_turn[1] + 1}], "reasoning": "This is a valid forward move."}}
        """
        nav_response = navigator.get_response(navigator_prompt)
        
        proposed_move_list = nav_response.get('move')
        
        if not is_valid_one_step_move(current_position_for_turn, proposed_move_list):
            print(f"Navigator proposed an INVALID move: {proposed_move_list}.")
            last_feedback = f"Invalid move. Your proposed move {proposed_move_list} was not one step away from {current_position_for_turn}."
            time.sleep(1)
            continue
            
        proposed_move = tuple(proposed_move_list)
        print(f"Navigator proposes: {proposed_move} (Reason: {nav_response.get('reasoning')})")

        move_result = env.move(proposed_move)
        
        if move_result == "Success":
            print("\nSUCCESS! The target has been reached.")
            return True

        guide_prompt = f"""
        You are Guide. You observe the environment.
        The Navigator was at {current_position_for_turn} and proposed moving to {proposed_move}.
        The result of this move was: "{move_result}".
        The Navigator's path so far has been: {path_string}
        
        Provide a brief, helpful critique as a JSON object.
        Example: {{"critique": "That move is blocked. You must find another way."}}
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
        
        if move_result == "Valid":
            path_history.append(env.position)

        time.sleep(1)

    print(f"\nFAILURE! The step limit of {MAX_STEPS} was reached. The team is likely stuck.")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Local Minima Trap experiment.")
    parser.add_argument('--os', type=str, choices=['none', 'ferro', 'boyd'], required=True,
                        help="Specify the feedback system: 'none', 'ferro', or 'boyd'.")
    
    args = parser.parse_args()

    if args.os == 'none':
        run_experiment(aether_os_script=None)
    elif args.os == 'ferro':
        run_experiment(aether_os_script="ferro_aether_os.py")
    elif args.os == 'boyd':
        run_experiment(aether_os_script="boyd_aether_os.py")
