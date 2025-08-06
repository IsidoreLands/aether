# experiri/baseline_runner.py
#
# The definitive baseline experiment runner.
# This is a self-contained script with no placeholders.
# 1. Uses a SOLID wall environment.
# 2. Empowers the HRM with feedback on its last action AND local wall data.

import json
import asyncio
import argparse
import os
import aiohttp
import torch
import numpy as np
import requests

# Alerts
NTFY_TOPIC = "roma"


def send_notification(title, message, priority="default", tags=None):
    """Sends a push notification to the specified ntfy.sh topic."""
    headers = {"Title": title, "Priority": priority, "Tags": tags if tags else ""}
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers=headers,
        )
    except Exception as e:
        # If ntfy fails, we don't want to crash the main experiment.
        print(f"--- WARNING: Failed to send notification: {e} ---")


# Assuming these files exist and are correct in their respective locations
from experiri.model_loader import load_player, HRMPlayer
from sagas.saga_generator import SagaGenerator

MAX_STEPS_PER_CYCLE = 24


class FortifiedGridEnvironment:
    """Represents the grid with a SOLID, inescapable wall."""

    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        # The wall is now a solid, impassable barrier.
        self.wall = [(5, y) for y in range(size)]

    def reset(self):
        """Resets the environment for a new trial."""
        self.position = self.start

    def get_local_env_state(self, pos):
        """Returns a numeric vector for adjacent wall/boundary cells."""
        r, c = pos
        # [up, down, left, right] -> 1.0 if blocked, 0.0 if open
        return [
            1.0 if (r - 1, c) in self.wall or r == 0 else 0.0,
            1.0 if (r + 1, c) in self.wall or r == self.size - 1 else 0.0,
            1.0 if (r, c - 1) in self.wall or c == 0 else 0.0,
            1.0 if (r, c + 1) in self.wall or c == self.size - 1 else 0.0,
        ]

    def move(self, new_position):
        """Processes a move and returns the result."""
        if not (isinstance(new_position, tuple) and len(new_position) == 2):
            return "InvalidFormat"
        if new_position in self.wall:
            return "Blocked"
        if not (0 <= new_position[0] < self.size and 0 <= new_position[1] < self.size):
            return "OutOfBounds"
        self.position = new_position
        if self.position == self.target:
            return "Success"
        return "Valid"


class DefinitiveHRMPlayer(HRMPlayer):
    """
    The definitive HRM player with combined senses. It is aware of its last
    action's result AND its immediate surroundings.
    """

    def __init__(self, config):
        # The input dimension is now richer to handle the new state.
        config["input_dim"] = (
            10  # [cur_r, cur_c, tar_r, tar_c, up, down, left, right, valid, blocked]
        )
        super().__init__(config)

    def _get_state_tensor(self, env_state):
        """Converts the full environment state dictionary into a tensor."""
        last_move_status = env_state["last_move_status"]
        # [valid, blocked]
        status_vec = [1.0, 0.0] if last_move_status == "Valid" else [0.0, 1.0]

        state_array = np.array(
            [
                *env_state["current_pos"],
                *env_state["target_pos"],
                *env_state["local_walls"],
                *status_vec,
            ],
            dtype=np.float32,
        )
        return torch.from_numpy(state_array).unsqueeze(0).to(self.device)

    async def get_response(self, state, session):
        """The get_response method now expects the state dictionary."""
        state_tensor = self._get_state_tensor(state)
        with torch.no_grad():
            move_tensor = self.model(state_tensor)

        direction = tuple(np.round(move_tensor.squeeze().cpu().numpy()).astype(int))
        dx = np.clip(direction[0], -1, 1)
        dy = np.clip(direction[1], -1, 1)

        proposed_pos = (state["current_pos"][0] + dx, state["current_pos"][1] + dy)
        return {"move": proposed_pos}


async def run_definitive_baseline_trial(hrm_agent, guide_agent):
    """Runs one full, independent trial of the baseline experiment."""
    env = FortifiedGridEnvironment()
    path_history = [env.start]
    last_move_status = "Valid"

    async with aiohttp.ClientSession() as session:
        for step in range(1, MAX_STEPS_PER_CYCLE + 1):
            current_pos = env.position

            # 1. Assemble the full state for the HRM
            hrm_state = {
                "current_pos": current_pos,
                "target_pos": env.target,
                "local_walls": env.get_local_env_state(current_pos),
                "last_move_status": last_move_status,
            }

            # 2. Get the HRM's proposed move
            hrm_response = await hrm_agent.get_response(hrm_state, session)
            proposed_move = hrm_response["move"]

            # 3. Process the move in the environment
            move_result = env.move(proposed_move)

            # 4. Update the status for the next loop
            last_move_status = move_result

            print(
                f"  Step {step} | Pos: {current_pos} | HRM Proposes: {proposed_move} | Result: {move_result}"
            )

            if move_result == "Success":
                path_history.append(env.position)
                print("\n  SUCCESS! Target reached in this baseline trial.")
                return {"path_history": path_history, "success": True}

            if move_result not in ["Blocked", "InvalidFormat", "OutOfBounds"]:
                path_history.append(env.position)

    print(f"\n  FAILURE! Step limit reached in this baseline trial.")
    return {"path_history": path_history, "success": False}


async def main():
    """Main function to orchestrate the entire baseline experiment."""
    parser = argparse.ArgumentParser(
        description="Run the DEFINITIVE BASELINE experiment."
    )
    parser.add_argument(
        "--trials", type=int, default=5, help="Number of independent trials to run."
    )
    parser.add_argument(
        "--hrm_key",
        type=str,
        default="hrm_definitive",
        help="Model key for the HRM agent.",
    )
    parser.add_argument(
        "--saga_key",
        type=str,
        default="ollama_phi3",
        help="Model key for Saga generation.",
    )
    args = parser.parse_args()

    # --- NOTIFICATION ON START ---
    start_message = f"Starting {args.trials}-trial definitive baseline experiment."
    send_notification(
        "Aether Experiment Started", start_message, priority="high", tags="rocket"
    )

    success_count = 0  # INITIALIZE THE COUNTER HERE

    try:
        print("=" * 50)
        print("      STARTING DEFINITIVE BASELINE TEST RUNNER")
        print("=" * 50)

        # Load agents
        with open("models/model_registry.json", "r") as f:
            registry = json.load(f)
        hrm_config = registry[args.hrm_key]
        hrm_agent = DefinitiveHRMPlayer(hrm_config)
        saga_generator = SagaGenerator(model_key=args.saga_key)

        print(f"Loaded Definitive HRM Agent: '{args.hrm_key}'")
        print(f"Loaded Saga Generator LLM: '{args.saga_key}'")

        os.makedirs("sagas/generated", exist_ok=True)

        # The main trial loop
        success_count = 0
        for i in range(args.trials):
            trial_num = i + 1
            print(f"\n{'='*20} TRIAL {trial_num}/{args.trials} {'='*20}")

            run_log = await run_definitive_baseline_trial(hrm_agent, None)
            if run_log.get("success", False):
                success_count += 1

            output_filename = (
                f"sagas/generated/definitive_baseline_run_{trial_num}.json"
            )
            await saga_generator.generate(run_log, output_filename)
            print(f"Generated '{output_filename}' for analysis.")

    except Exception as e:
        # --- NOTIFICATION ON CRASH ---
        error_message = f"Experiment crashed with error: {e}"
        print(f"\n--- FATAL ERROR: {error_message} ---")
        send_notification(
            "Aether Experiment CRASHED", error_message, priority="urgent", tags="x"
        )
        # Re-raise the exception so we still see the traceback
        raise

    finally:
        # --- NOTIFICATION ON COMPLETION ---
        completion_message = f"Experiment finished. {success_count}/{args.trials} trials were successful."
        print("\n" + "=" * 50)
        print("      ALL DEFINITIVE BASELINE TRIALS COMPLETE")
        print(f"      Success Rate: {success_count}/{args.trials}")
        print("=" * 50)
        send_notification(
            "Aether Experiment Complete",
            completion_message,
            priority="high",
            tags="tada",
        )


if __name__ == "__main__":
    asyncio.run(main())
