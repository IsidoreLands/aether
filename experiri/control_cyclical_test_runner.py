# experiri/control_cyclical_test_runner.py
#
# This script runs a CONTROLLED, BASELINE experiment. It manages multiple
# independent test runs but INTENTIONALLY DOES NOT pass the generated Saga
# as context to subsequent runs. This establishes a baseline performance
# for the Navigator-Guide system without the SAGA learning loop.

import json
import asyncio
import argparse
import os
import aiohttp

# Use the new model loader and saga generator
from experiri.model_loader import load_player
from sagas.saga_generator import SagaGenerator

# --- Core Logic Imported from the local_minima_test ---
MAX_STEPS_PER_CYCLE = 25

class GridEnvironment:
    """Represents the real grid, the trap, and the agent's state."""
    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        self.wall = [(5, y) for y in range(size) if y != 5]

    def reset(self):
        """Resets the environment for a new run."""
        self.position = self.start

    def move(self, new_position):
        """Attempts to move, checking for walls and success."""
        if new_position in self.wall:
            return "Blocked"
        if not (0 <= new_position[0] < self.size and 0 <= new_position[1] < self.size):
            return "OutOfBounds"
        self.position = new_position
        if self.position == self.target:
            return "Success"
        return "Valid"

async def run_baseline_navigation_test(hrm_agent, guide_agent):
    """
    Runs one full, independent navigation test.
    Crucially, this function does NOT accept a saga_context.
    Returns a run_log dictionary.
    """
    print(f"\n--- Running Baseline Navigation Test ---")
    print("Context: No Saga provided (as per baseline protocol).")

    env = GridEnvironment()
    path_history = [env.start]

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS_PER_CYCLE + 1):
            current_pos = env.position
            print(f"  Step {step}/{MAX_STEPS_PER_CYCLE} | Position: {current_pos}")

            # 1. HRM agent (Navigator) proposes a move based on its current state.
            hrm_response = await hrm_agent.get_response(prompt=None, session=session, env=env)
            proposed_move = tuple(hrm_response['move'])
            
            # 2. LLM Guide critiques the move without any historical memory.
            path_str = " -> ".join(map(str, path_history[-5:]))
            guide_prompt = (
                f"You are a Guide. A Navigator at {current_pos} proposes moving to {proposed_move}.\n"
                f"Its recent path is ...{path_str}. The goal is {env.target}. A wall exists at x=5.\n"
                f"Provide a brief, reactive critique of this single move.\n"
                f"Respond with only a JSON object: {{\"critique\": \"...\"}}"
            )
            guide_response = await guide_agent.get_response(guide_prompt, session)
            critique = guide_response.get('critique', "Critique failed.")
            print(f"    Guide ({guide_agent.model_name}) critiques: {critique}")
            
            # 3. Environment processes the move.
            move_result = env.move(proposed_move)
            
            if move_result == "Success":
                print("\n  SUCCESS! Target reached in this baseline trial.")
                path_history.append(env.position)
                return {'path_history': path_history, 'success': True}

            if move_result != "Blocked":
                 path_history.append(env.position)

    print(f"\n  FAILURE! Step limit reached in this baseline trial.")
    return {'path_history': path_history, 'success': False}


async def run_control_experiment(num_trials: int, hrm_model_key: str, guide_model_key: str, saga_model_key: str):
    """
    Orchestrates the baseline experiment, running multiple independent trials.
    """
    print("="*50)
    print("      STARTING CONTROLLED BASELINE TEST RUNNER")
    print("="*50)

    # 1. Load all required agents
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

    # 2. Initialize output directory
    saga_filename_template = "sagas/generated/baseline_run_{trial}.json"
    os.makedirs("sagas/generated", exist_ok=True)

    # 3. The main trial loop
    for i in range(num_trials):
        trial_num = i + 1
        print(f"\n{'='*20} TRIAL {trial_num}/{num_trials} {'='*20}")

        # Run the baseline test. Note that no context is passed in.
        run_log = await run_baseline_navigation_test(hrm_agent, guide_agent)

        # Generate a Saga for this run (for data analysis), but do not use it again.
        output_filename = saga_filename_template.format(trial=trial_num)
        await saga_generator.generate(run_log, output_filename)
        
        print(f"Generated '{output_filename}' for analysis. No context will be carried forward.")
        
    print("\n" + "="*50)
    print("      ALL BASELINE TRIALS COMPLETE")
    print("="*50)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the BASELINE SAGA experiment (no learning between trials).")
    parser.add_argument('--trials', type=int, default=3, help="Number of independent trials to run.")
    parser.add_argument('--hrm_key', type=str, default='hrm_baseline', help="Model key for the HRM agent.")
    parser.add_argument('--guide_key', type=str, default='ollama_phi3', help="Model key for the Guide LLM.")
    parser.add_argument('--saga_key', type=str, default='ollama_phi3', help="Model key for the Saga generation LLM.")
    
    args = parser.parse_args()
    
    asyncio.run(run_control_experiment(args.trials, args.hrm_key, args.guide_key, args.saga_key))
