# experiri/cyclical_runner.py (Final Corrected Version)

import sys
import os
import json
import asyncio
import argparse
import aiohttp
import torch
import numpy as np
import requests 

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from flux_core import FluxCore
from experiri.model_loader import load_player
from sagas.saga_generator import SagaGenerator
from experiri.baseline_runner import FortifiedGridEnvironment

MAX_STEPS_PER_CYCLE = 30
NTFY_TOPIC = "roma"
CYCLE_NAMES = ["Departure", "Trials", "Crucible", "Return", "Ascension"]

def send_notification(title, message, priority="default", tags=None):
    headers = {"Title": title, "Priority": priority, "Tags": tags if tags else ""}
    try: requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'), headers=headers)
    except Exception as e: print(f"--- WARNING: Failed to send notification: {e} ---")

def text_to_amp(text):
    return np.log1p(sum(ord(c) for c in text))

async def run_aetheric_learning_trial(hrm_agent, guide_agent, agent_animus, saga_context=None, all_past_sagas=None):
    env = FortifiedGridEnvironment()
    path_history, last_move_status = [env.start], "Valid"
    guide_critiques = []
    consecutive_failures = 0
    last_proposed_move = None

    print(f"\n--- Running Aetheric Learning Trial ---")
    print("Context: Saga from previous run provided." if saga_context else "Context: No Saga provided (first run).")

    if saga_context:
        saga_text = " ".join(saga_context)
        agent_animus.perturb(np.random.randint(0, agent_animus.size-1), 
                             np.random.randint(0, agent_animus.size-1), 
                             text_to_amp(saga_text))
    agent_animus.converge()
    print(f"  Animus State: R={agent_animus.resistance:.2e}, C={agent_animus.capacitance:.2f}, M={agent_animus.magnetism:.2f}")

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS_PER_CYCLE + 1):
            current_pos = env.position
            
            lifeline_context = None
            if consecutive_failures >= 3 and all_past_sagas:
                print(f"  !!! LIFELINE TRIGGERED !!!")
                lifeline_context = [cmd for saga in all_past_sagas for cmd in saga]
                consecutive_failures = 0

            hrm_state = {
                'current_pos': current_pos, 'target_pos': env.target,
                'local_walls': env.get_local_env_state(current_pos),
                'last_move_status': last_move_status, 'saga_context': saga_context,
                'lifeline_context': lifeline_context, 'animus_sextet': agent_animus.get_sextet()
            }

            hrm_response = await hrm_agent.get_response(hrm_state, session)
            proposed_move = hrm_response['move']
            
            # --- LOGIC FIX: First, get the result of the move ---
            move_result = env.move(proposed_move)
            print(f"  Step {step} | Pos: {current_pos} | HRM Proposes: {proposed_move} | Result: {move_result}")

            # --- THEN, decide if a critique is needed ---
            critique_text = ""
            if move_result == "Blocked" or (proposed_move == last_proposed_move and current_pos == path_history[-1]):
                print("  -> Guide intervention triggered.")
                guide_prompt = f"Agent at {current_pos} is stuck, proposing move to {proposed_move}. Goal is {env.target}, wall at x=5. Provide a brief, strategic critique as a JSON object: {{\"critique\": \"...\"}}"
                guide_response = await guide_agent.get_response(guide_prompt, session)
                guide_critiques.append(guide_response)
                critique_text = guide_response.get('critique', '')
            
            last_proposed_move = proposed_move
            last_move_status = move_result
            
            if critique_text:
                agent_animus.perturb(np.random.randint(0, agent_animus.size-1), 
                                     np.random.randint(0, agent_animus.size-1),
                                     text_to_amp(critique_text) * -0.5)
                agent_animus.converge()
            
            if move_result == "Blocked": consecutive_failures += 1
            else: consecutive_failures = 0

            if move_result == "Success":
                path_history.append(env.position)
                print("\n  SUCCESS! The agent has learned to solve the trap.")
                return {'path_history': path_history, 'success': True, 'critiques': guide_critiques}

            if move_result not in ["Blocked", "InvalidFormat", "OutOfBounds"]:
                path_history.append(env.position)

    print(f"\n  FAILURE! Step limit reached in this learning trial.")
    return {'path_history': path_history, 'success': False, 'critiques': guide_critiques}


async def main():
    # ... (main function is unchanged and correct)
    parser = argparse.ArgumentParser(description="Run the SAGA v3.0 AETHERIC LEARNING experiment.")
    parser.add_argument('--cycles', type=int, default=5, help="Number of learning cycles.")
    parser.add_argument('--hrm_key', type=str, default='ARC', help="Key for the ARC agent.")
    parser.add_argument('--guide_key', type=str, default='hf_phi3', help="Key for the Guide LLM.")
    parser.add_argument('--saga_key', type=str, default='hf_phi3', help="Key for Saga generation.")
    args = parser.parse_args()
    start_message = f"Starting {args.cycles}-cycle AETHERIC learning experiment."; send_notification("Aether Learning Started", start_message, priority="high", tags="brain")
    success_count = 0
    try:
        print("="*50); print("      STARTING AETHERIC SAGA LEARNING RUNNER"); print("="*50)
        hrm_agent = load_player(args.hrm_key); guide_agent = load_player(args.guide_key); saga_generator = SagaGenerator(model_key=args.saga_key)
        agent_animus = FluxCore()
        os.makedirs("sagas/generated", exist_ok=True)
        saga_context = None; all_sagas = []
        for i in range(args.cycles):
            cycle_num = i + 1; cycle_name = CYCLE_NAMES[i] if i < len(CYCLE_NAMES) else f"Cycle {cycle_num}"
            print(f"\n{'='*20} CYCLE {cycle_num}/{args.cycles} ({cycle_name}) {'='*20}")
            past_sagas_for_lifeline = all_sagas if cycle_name not in ["Departure", "Trials"] else None
            run_log = await run_aetheric_learning_trial(hrm_agent, guide_agent, agent_animus, saga_context, past_sagas_for_lifeline)
            if run_log.get('success'): success_count += 1
            output_filename = f"sagas/generated/aetheric_run_{cycle_num}.json"
            await saga_generator.generate(run_log, run_log['critiques'], output_filename, max_retries=2)
            try:
                with open(output_filename, 'r') as f: new_saga = json.load(f); saga_context = new_saga; all_sagas.append(new_saga)
                print(f"Loaded '{output_filename}' as context for the next cycle.")
            except Exception: print(f"Could not load Saga. Proceeding without context."); saga_context = None
    except Exception as e:
        error_message = f"Learning experiment CRASHED: {e}"; print(f"\n--- FATAL ERROR: {error_message} ---")
        send_notification("Aether Learning CRASHED", error_message, priority="urgent", tags="x"); raise
    finally:
        completion_message = f"Aetheric learning complete. {success_count}/{args.cycles} cycles successful."
        print("\n" + "="*50); print("      ALL AETHERIC CYCLES COMPLETE"); print(f"      Success Rate: {success_count}/{args.cycles}"); print("="*50)
        send_notification("Aether Learning Complete", completion_message, priority="high", tags="tada")

if __name__ == '__main__':
    asyncio.run(main())
