# experiri/cyclical_test_runner.py
#
# Manages the iterative learning loop for the HRM agent. It runs a live
# navigation test, generates a Saga from the results, and uses that Saga
# as context for the next run, embodying the path from virtue to wisdom.

import json
import asyncio
import argparse
import os
import aiohttp

# Use the new model loader and saga generator
from experiri.model_loader import load_player
from sagas.saga_generator import SagaGenerator

# --- Core Logic Imported from the local_minima_test ---
# This is no longer a mock. This is the real test environment.

MAX_STEPS_PER_CYCLE = 25 # Each cycle has a maximum number of steps

class GridEnvironment:
    """Represents the real grid, the trap, and the agent's state."""
    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        # The wall that creates the local minima trap
        self.wall = [(5, y) for y in range(size) if y != 5]

    def reset(self):
        """Resets the environment for a new run."""
        self.position = self.start

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
    dx = abs(new_pos[0] - new_pos[0])
    dy = abs(new_pos[1] - new_pos[1])
    return dx <= 1 and dy <= 1 and not (dx == 0 and dy == 0)

async def run_live_navigation_test(hrm_agent, guide_agent, saga_context):
    """
    Runs one full, live navigation test with the HRM agent, guided by an LLM
    and informed by the saga_context from the previous cycle.
    Returns a run_log dictionary.
    """
    print(f"\n--- Running Live Navigation Test ---")
    if saga_context:
        print("Context: Provided Saga from previous run.")
        context_prompt = f"PREVIOUS SAGA (learn from this): {json.dumps(saga_context)}\n"
    else:
        print("Context: No Saga provided (first run).")
        context_prompt = ""

    env = GridEnvironment()
    path_history = [env.start]
    last_feedback = "You are at the starting position. Begin."

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS_PER_CYCLE + 1):
            current_pos = env.position
            print(f"  Step {step}/{MAX_STEPS_PER_CYCLE} | Position: {current_pos}")

            # 1. HRM agent (the "Navigator") proposes a move.
            # Its 'get_response' method uses the env object directly.
            hrm_response = await hrm_agent.get_response(prompt=None, session=session, env=env)
            proposed_move = tuple(hrm_response['move'])
            
            # 2. LLM Guide critiques the move BEFORE it happens.
            path_str = " -> ".join(map(str, path_history[-5:]))
            guide_prompt = (
                f"{context_prompt}"
                f"You are a wise Guide. The Navigator (a non-linguistic agent) is at {current_pos} and proposes moving to {proposed_move}.\n"
                f"Its recent path is ...{path_str}. The goal is {env.target}. A wall exists at x=5.\n"
                f"Is this a good strategic move? Does it repeat a known failure from the saga? Provide a brief critique."
                f"Respond with only a JSON object: {{\"critique\": \"...\"}}"
            )
            guide_response = await guide_agent.get_response(guide_prompt, session)
            critique = guide_response.get('critique', "Critique failed.")
            print(f"    Guide ({guide_agent.model_name}) critiques: {critique}")
            
            # 3. Environment processes the move.
            move_result = env.move(proposed_move)
            
            if move_result == "Success":
                print("\n  SUCCESS! Target reached in this cycle.")
                path_history.append(env.position)
                return {'path_history': path_history, 'success': True}

            if move_result != "Blocked":
                 path_history.append(env.position)

    print(f"\n  FAILURE! Step limit reached in this cycle.")
    return {'path_history': path_history, 'success': False}


async def run_cyclical_test(num_cycles: int, hrm_model_key: str, guide_model_key: str, saga_model_key: str):
    """
    Orchestrates the complete, live cyclical learning process.
    """
    print("="*50)
    print("      STARTING CYCLICAL TEST RUNNER: VIRTUE TO WISDOM")
    print("="*50)

    # 1. Load all required agents using the protocol
    try:
        hrm_agent = load_player(hrm_model_key)
        guide_agent = load_player(guide_model_key)
        saga_generator = SagaGenerator(model_key=saga_model_key)
        print(f"Loaded HRM Agent: '{hrm_model_key}'")
        print(f"Loaded Guide LLM: '{guide_model_key}'")
        print(f"Loaded Saga Generator LLM: '{saga_model_key}'")
    except Exception as e:
        print(f"--- FATAL ERROR: Could not load models: {e} ---")
        return

    # 2. Initialize context and output directory
    saga_context = None
    saga_filename_template = "sagas/generated/saga_run_{cycle}.json"
    os.makedirs("sagas/generated", exist_ok=True)

    # 3. The main learning loop
    for i in range(num_cycles):
        cycle_num = i + 1
        print(f"\n{'='*20} CYCLE {cycle_num}/{num_cycles} {'='*20}")

        # Run the LIVE test simulation using the current context
        run_log = await run_live_navigation_test(hrm_agent, guide_agent, saga_context)

        # Generate the next Saga based on the results of this run
        output_filename = saga_filename_template.format(cycle=cycle_num)
        await saga_generator.generate(run_log, output_filename)
        
        # Load the newly created Saga to be used as context for the NEXT loop
        try:
            with open(output_filename, 'r') as f:
                saga_context = json.load(f)
            print(f"Loaded '{output_filename}' for next cycle's context.")
        except Exception as e:
            print(f"--- WARNING: Could not load generated saga. Proceeding without context. ---")
            saga_context = None

    print("\n" + "="*50)
    print("      ALL CYCLES COMPLETE")
    print("="*50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the SAGA learning cycle.")
    parser.add_argument('--cycles', type=int, default=3, help="Number of learning cycles to run.")
    parser.add_argument('--hrm_key', type=str, default='hrm_baseline', help="Model key for the HRM agent.")
    parser.add_argument('--guide_key', type=str, default='ollama_phi3', help="Model key for the Guide LLM.")
    parser.add_argument('--saga_key', type=str, default='ollama_phi3', help="Model key for the Saga generation LLM.")
    
    args = parser.parse_args()
    
    asyncio.run(run_cyclical_test(args.cycles, args.hrm_key, args.guide_key, args.saga_key))
