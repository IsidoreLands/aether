# experiri/cyclical_runner.py
#
# Manages the full SAGA learning loop. It runs a test with a Saga-aware agent,
# generates a new Saga, and passes it as context for the next run, enabling
# the agent to learn from its history.

import json
import asyncio
import argparse
import os
import aiohttp
import torch
import numpy as np
import requests # For ntfy

# Import our definitive components
from experiri.model_loader import load_player
from sagas.saga_generator import SagaGenerator
from experiri.baseline_runner import FortifiedGridEnvironment, DefinitiveHRMPlayer

MAX_STEPS_PER_CYCLE = 30 # Give it a few extra steps to find a solution

# --- ntfy Notification Setup ---
NTFY_TOPIC = "roma"
def send_notification(title, message, priority="default", tags=None):
    """Sends a push notification to the specified ntfy.sh topic."""
    headers = {"Title": title, "Priority": priority, "Tags": tags if tags else ""}
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'), headers=headers)
    except Exception as e:
        print(f"--- WARNING: Failed to send notification: {e} ---")

# --- NEW: The Saga-Aware HRM Player ---
class SagaAwareHRMPlayer(DefinitiveHRMPlayer):
    """
    An evolution of the HRM player that can process an abstract, linguistic
    Saga into its state vector, allowing it to learn from history.
    """
    def __init__(self, config):
        # We add 4 more dimensions for the saga context embedding
        config['input_dim'] = 14 # 10 (base state) + 4 (saga embedding)
        super().__init__(config)

    def _embed_saga(self, saga_context):
        """A simple method to convert a Saga (list of strings) into a numeric vector."""
        if not saga_context:
            return [0.0, 0.0, 0.0, 0.0] # Neutral context

        # Simple embedding: count keywords related to failure, success, movement
        text = " ".join(saga_context).upper()
        failure_score = text.count("REDIMO") + text.count("FAILURE")
        success_score = text.count("OSTENDO") + text.count("SUCCESS")
        
        # A crude measure of "stuckness"
        stuck_score = 0
        if "BLOCKED" in text and failure_score > 0:
             # Count how many times it was blocked
             stuck_score = text.count("BLOCKED") / 10.0 # Normalize

        # A measure of exploration/movement
        move_score = text.count("PERTURBO") / 20.0 # Normalize
        
        return [
            np.clip(failure_score, 0, 1),
            np.clip(success_score, 0, 1),
            np.clip(stuck_score, 0, 1),
            np.clip(move_score, 0, 1)
        ]

    def _get_state_tensor(self, env_state):
        """Converts the full environment state, including the Saga, into a tensor."""
        saga_embedding = self._embed_saga(env_state['saga_context'])
        
        # Standard 10D state from the definitive player
        status_vec = [1.0, 0.0] if env_state['last_move_status'] == "Valid" else [0.0, 1.0]
        base_state_array = np.array([
            *env_state['current_pos'], *env_state['target_pos'],
            *env_state['local_walls'], *status_vec
        ], dtype=np.float32)

        # Concatenate the base state with the saga embedding
        full_state_array = np.concatenate([base_state_array, np.array(saga_embedding, dtype=np.float32)])
        return torch.from_numpy(full_state_array).unsqueeze(0).to(self.device)


async def run_learning_trial(hrm_agent, guide_agent, saga_context=None):
    """Runs one trial of the experiment, using the provided Saga as context."""
    env = FortifiedGridEnvironment()
    path_history = [env.start]
    last_move_status = "Valid"

    print(f"\n--- Running Learning Trial ---")
    if saga_context:
        print("Context: Saga from previous run has been provided.")
    else:
        print("Context: No Saga provided (first run).")

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS_PER_CYCLE + 1):
            current_pos = env.position
            
            # The full state now includes the historical saga context
            hrm_state = {
                'current_pos': current_pos, 'target_pos': env.target,
                'local_walls': env.get_local_env_state(current_pos),
                'last_move_status': last_move_status,
                'saga_context': saga_context
            }

            hrm_response = await hrm_agent.get_response(hrm_state, session)
            proposed_move = hrm_response['move']
            move_result = env.move(proposed_move)
            last_move_status = move_result

            # The guide is no longer needed in the loop, but we could add it back for richer sagas
            print(f"  Step {step} | Pos: {current_pos} | HRM Proposes: {proposed_move} | Result: {move_result}")

            if move_result == "Success":
                path_history.append(env.position)
                print("\n  SUCCESS! The agent has learned to solve the trap.")
                return {'path_history': path_history, 'success': True}

            if move_result not in ["Blocked", "InvalidFormat", "OutOfBounds"]:
                path_history.append(env.position)

    print(f"\n  FAILURE! Step limit reached in this learning trial.")
    return {'path_history': path_history, 'success': False}


async def main():
    parser = argparse.ArgumentParser(description="Run the SAGA LEARNING experiment.")
    parser.add_argument('--cycles', type=int, default=5, help="Number of learning cycles to run.")
    parser.add_argument('--hrm_key', type=str, default='hrm_definitive', help="Key for the HRM agent config.")
    parser.add_argument('--saga_key', type=str, default='ollama_phi3', help="Model key for Saga generation.")
    args = parser.parse_args()

    start_message = f"Starting {args.cycles}-cycle SAGA learning experiment."
    send_notification("Aether Learning Started", start_message, priority="high", tags="brain")
    
    success_count = 0
    try:
        print("="*50)
        print("      STARTING SAGA LEARNING RUNNER")
        print("="*50)

        # We load the HRM config, but instantiate our new Saga-aware player
        with open('models/model_registry.json', 'r') as f:
            registry = json.load(f)
        hrm_config = registry[args.hrm_key]
        hrm_agent = SagaAwareHRMPlayer(hrm_config)
        saga_generator = SagaGenerator(model_key=args.saga_key)

        os.makedirs("sagas/generated", exist_ok=True)
        saga_context = None

        for i in range(args.cycles):
            cycle_num = i + 1
            print(f"\n{'='*20} CYCLE {cycle_num}/{args.cycles} {'='*20}")
            run_log = await run_learning_trial(hrm_agent, None, saga_context)
            if run_log.get('success'):
                success_count += 1

            output_filename = f"sagas/generated/learning_run_{cycle_num}.json"
            await saga_generator.generate(run_log, output_filename, max_retries=2)

            try:
                with open(output_filename, 'r') as f:
                    saga_context = json.load(f)
                print(f"Loaded '{output_filename}' as context for the next cycle.")
            except Exception:
                print(f"Could not load Saga from {output_filename}. Proceeding without context."); saga_context = None
    
    except Exception as e:
        error_message = f"Learning experiment CRASHED: {e}"
        print(f"\n--- FATAL ERROR: {error_message} ---")
        send_notification("Aether Learning CRASHED", error_message, priority="urgent", tags="x")
        raise
    
    finally:
        completion_message = f"Learning complete. {success_count}/{args.cycles} cycles were successful."
        print("\n" + "="*50)
        print("      ALL LEARNING CYCLES COMPLETE")
        print(f"      Success Rate: {success_count}/{args.cycles}")
        print("="*50)
        send_notification("Aether Learning Complete", completion_message, priority="high", tags="tada")


if __name__ == '__main__':
    asyncio.run(main())
