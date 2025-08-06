# experiri/local_minima_test.py
# A model-agnostic script to test agent collaboration in a local minima trap.

import asyncio
import aiohttp
import json
import time
import argparse

# Import our new factory function to load any player
from experiri.model_loader import load_player

# Import AetherOS versions dynamically later
# Note: No hardcoded model names or player classes here!

MAX_STEPS = 25

class GridEnvironment:
    """Represents the conceptual grid, the trap, and the players' state."""
    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        # A wall that creates the trap
        self.wall = [(5, y) for y in range(size) if y != 5]

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

def is_valid_one_step_move(current_pos, new_pos):
    """Checks if a move is a valid single step away."""
    if not isinstance(new_pos, (list, tuple)) or len(new_pos) != 2: return False
    dx = abs(new_pos[0] - current_pos[0])
    dy = abs(new_pos[1] - current_pos[1])
    return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

async def run_experiment(aether_os_script, nav_key, guide_key):
    """Main async function to run one full iteration of the experiment."""
    print("\n" + "="*50)
    
    # --- AetherOS Setup ---
    aether_context = None
    if aether_os_script:
        if aether_os_script == "boyd":
            from versiones.boyd_aether_os import Contextus
            aether_context = Contextus()
        elif aether_os_script == "ferro":
            from versiones.ferro_aether_os import Contextus
            aether_context = Contextus()
        else: # 'base' AetherOS
            import aether_os
            aether_context = aether_os.Contextus()

        print(f"Running Experiment WITH {aether_os_script} AetherOS Feedback")
        aether_context.execute_command("CREO 'ENVIRONMENT'")
        aether_context.execute_command("FOCUS 'ENVIRONMENT'")
    else:
        print("Running Experiment WITHOUT AetherOS Feedback (Control)")
    
    print(f"  Navigator: '{nav_key}' | Guide: '{guide_key}'")
    print("="*50 + "\n")

    # --- Player and Environment Setup ---
    env = GridEnvironment()
    try:
        # MODEL-AGNOSTIC: Load players using the factory
        navigator = load_player(nav_key)
        guide = load_player(guide_key)
    except (FileNotFoundError, ValueError, NotImplementedError) as e:
        print(f"--- SETUP FAILED: {e} ---")
        return

    path_history = [env.start]
    last_feedback = "You are at the starting position. Begin."

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS + 1):
            current_pos = env.position
            print(f"--- Step {step}/{MAX_STEPS} | Position: {current_pos} ---")

            path_str = " -> ".join(map(str, path_history[-10:])) # Show recent path

            # 1. Navigator proposes a move
            nav_prompt = (
                f"You are Navigator. Goal: {env.target}. Current: {current_pos}.\n"
                f"Recent path: ...{path_str}\nLast feedback: \"{last_feedback}\"\n"
                f"RULES: Propose a move one step away (including diagonals). Do not repeat recent positions.\n"
                f"Respond with only a JSON object: {{\"move\": [x, y], \"reasoning\": \"...\"}}"
            )
            # Pass the session and env to the player; it will use what it needs.
            nav_response = await navigator.get_response(nav_prompt, session, env)
            
            proposed_move_list = nav_response.get('move')
            if not is_valid_one_step_move(current_pos, proposed_move_list):
                print(f"  INVALID MOVE by {nav_key}: {proposed_move_list}. Retrying.")
                last_feedback = f"Invalid move. Your proposal {proposed_move_list} was not one valid step."
                continue
            
            proposed_move = tuple(proposed_move_list)
            print(f"  Navigator ({nav_key}) proposes: {proposed_move}")

            # 2. Guide critiques the move BEFORE it happens
            guide_prompt = (
                f"You are Guide. Navigator at {current_pos} wants to move to {proposed_move}.\n"
                f"Recent path: ...{path_str}\nIs this a good strategic move? Does it repeat a loop?\n"
                f"Respond with only a JSON object: {{\"critique\": \"...\"}}"
            )
            guide_response = await guide.get_response(guide_prompt, session, env)
            critique = guide_response.get('critique', "Critique failed.")
            print(f"  Guide ({guide_key}) critiques: {critique}")

            # 3. Environment processes the move
            move_result = env.move(proposed_move)
            print(f"  Environment result: {move_result}")

            if move_result == "Success":
                print("\nSUCCESS! Target reached.")
                path_history.append(env.position)
                # Here you could save the successful path_history
                return
            
            # 4. AetherOS processes feedback
            if aether_context:
                aether_command = f"PERTURBO 'Navigator proposed {proposed_move}, Guide critiqued: {critique}, Result was {move_result}'"
                last_feedback = aether_context.execute_command(aether_command)
                print(f"  AetherOS provides: {last_feedback}")
            else:
                last_feedback = f"Critique: {critique}. Result: {move_result}."
            
            if move_result != "Blocked":
                path_history.append(env.position)
            
            await asyncio.sleep(1) # Rate limit

    print(f"\nFAILURE! Step limit reached. Final path: {path_history}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the model-agnostic Local Minima Trap experiment.")
    parser.add_argument('--os', type=str, default='none', choices=['none', 'base', 'ferro', 'boyd'],
                        help="Specify the AetherOS feedback system.")
    parser.add_argument('--navigator', type=str, required=True,
                        help="Key for the Navigator model from model_registry.json (e.g., hrm_baseline).")
    parser.add_argument('--guide', type=str, required=True,
                        help="Key for the Guide model from model_registry.json (e.g., local_mixtral).")
    
    args = parser.parse_args()
    
    asyncio.run(run_experiment(args.os, args.navigator, args.guide))
