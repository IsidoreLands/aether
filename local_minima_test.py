# local_minima_test.py
#
# Description:
# This script runs a controlled experiment to test if different versions of the
# AetherOS can help two collaborating LLMs escape a "local minima trap".
# This version uses asyncio and aiohttp for robust, non-blocking API calls.

import json
import time
import argparse
import os
from dotenv import load_dotenv
import asyncio
import aiohttp

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
HF_API_ENDPOINT = "https://api-inference.huggingface.co/models/"
NAVIGATOR_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
GUIDE_MODEL = "google/gemma-7b-it" 
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

class HuggingFaceHubPlayer:
    """An async client for the Hugging Face Inference API."""
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = os.getenv("HF_TOKEN")
        if not self.api_key:
            raise ValueError("HF_TOKEN not found in .env file.")
        self.endpoint = f"{HF_API_ENDPOINT}{self.model_name}"

    async def get_response(self, prompt, session):
        """Sends a prompt to the HF API asynchronously."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "inputs": f"<s>[INST] {prompt} [/INST]", # Format for instruction-tuned models
            "parameters": {"return_full_text": False, "max_new_tokens": 150, "temperature": 0.7}
        }
        
        try:
            async with session.post(self.endpoint, headers=headers, json=payload, timeout=120) as response:
                response.raise_for_status()
                response_data = await response.json()
                
                response_text = response_data[0]['generated_text']
                
                decoder = json.JSONDecoder()
                start_index = response_text.find('{')
                if start_index == -1:
                    raise ValueError("No JSON object found in the response.")
                
                obj, _ = decoder.raw_decode(response_text[start_index:])
                return obj

        except Exception as e:
            print(f"\n--- ERROR communicating with {self.model_name}: {e} ---")
            return {"move": None, "reasoning": f"Error: {e}", "critique": f"Error: {e}"}

def is_valid_one_step_move(current_pos, new_pos):
    """Checks if a move is a valid single step."""
    if not isinstance(new_pos, (list, tuple)) or len(new_pos) != 2: return False
    dx = abs(new_pos[0] - current_pos[0])
    dy = abs(new_pos[1] - current_pos[1])
    return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

async def run_experiment(aether_os_script):
    """Main async function to run one full iteration of the experiment."""
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
    navigator = HuggingFaceHubPlayer(NAVIGATOR_MODEL)
    guide = HuggingFaceHubPlayer(GUIDE_MODEL)
    
    path_history = [env.start]
    last_feedback = "You are at the starting position. Begin."

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS + 1):
            current_position_for_turn = env.position
            print(f"--- Step {step}/{MAX_STEPS} ---")
            print(f"Current Position: {current_position_for_turn}")

            path_string = " -> ".join(map(str, path_history))
            recent_path = path_history[-5:]

            # 1. Navigator proposes a move
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
            nav_response = await navigator.get_response(navigator_prompt, session)
            proposed_move_list = nav_response.get('move')
            
            if not is_valid_one_step_move(current_position_for_turn, proposed_move_list):
                print(f"Navigator proposed an INVALID move: {proposed_move_list}.")
                last_feedback = f"Invalid move. Your proposed move {proposed_move_list} was not one step away from {current_position_for_turn}."
                await asyncio.sleep(1)
                continue
                
            proposed_move = tuple(proposed_move_list)
            print(f"Navigator proposes: {proposed_move} (Reason: {nav_response.get('reasoning')})")

            move_result = env.move(proposed_move)
            
            if move_result == "Success":
                print("\nSUCCESS! The target has been reached.")
                return True

            # 2. Guide critiques the move
            guide_prompt = f"""
            You are Guide. You observe the environment.
            The Navigator was at {current_position_for_turn} and proposed moving to {proposed_move}.
            The result of this move was: "{move_result}".
            The Navigator's path so far has been: {path_string}
            
            Provide a brief, helpful critique as a JSON object.
            Example: {{"critique": "That move is blocked. You must find another way."}}
            """
            guide_response = await guide.get_response(guide_prompt, session)
            critique = guide_response.get('critique', "Critique failed.")
            print(f"Guide critiques: {critique}")

            # 3. Generate final feedback for the next turn
            if aether_context and move_result == "Blocked":
                aether_command = f"PERTURBO '{critique}'"
                last_feedback = aether_context.execute_command(aether_command)
                print(f"AetherOS Feedback: {last_feedback}")
            else:
                last_feedback = critique
            
            if move_result == "Valid":
                path_history.append(env.position)

            await asyncio.sleep(1)

    print(f"\nFAILURE! The step limit of {MAX_STEPS} was reached. The team is likely stuck.")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Local Minima Trap experiment.")
    parser.add_argument('--os', type=str, choices=['none', 'aether', 'boyd'], required=True,
                        help="Specify the feedback system: 'none', 'aether', or 'boyd'.")
    
    args = parser.parse_args()

    # Run the main async function
    if args.os == 'none':
        asyncio.run(run_experiment(aether_os_script=None))
    elif args.os == 'aether':
        asyncio.run(run_experiment(aether_os_script="aether_os.py"))
    elif args.os == 'boyd':
        asyncio.run(run_experiment(aether_os_script="boyd_aether_os.py"))
