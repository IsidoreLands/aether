# sagas/saga_generator.py
# This module generates a narrative Saga from a test run log using a
# model from the central registry. (Corrected and Hardened)

import json
import asyncio
import aiohttp
import argparse
from experiri.model_loader import load_player


class SagaGenerator:
    """Generates a narrative Saga from a test run log."""

    def __init__(self, model_key=None):
        if model_key:
            self.player = load_player(model_key)
        else:
            self.player = self.prompt_for_player()

        if self.player:
            print(
                f"SagaGenerator initialized with player for model: {self.player.model_name}"
            )

    def prompt_for_player(self):
        print("\n--- Model Selection for Saga Generation ---")
        try:
            with open("models/model_registry.json", "r") as f:
                registry = json.load(f)
            llm_keys = [k for k, v in registry.items() if v.get("type") != "hrm"]
            print("Available models:")
            for i, key in enumerate(llm_keys):
                print(f"  {i+1}: {key}")
            while True:
                choice = input(f"Select a model by number (1-{len(llm_keys)}): ")
                if choice.isdigit() and 1 <= int(choice) <= len(llm_keys):
                    return load_player(llm_keys[int(choice) - 1])
                else:
                    print("Invalid selection. Please try again.")
        except Exception as e:
            print(f"Could not load models from registry: {e}")
            return None

    def _build_prompt(self, run_log):
        """Builds a detailed and 'hardened' prompt to ensure valid JSON output."""
        path_string = " -> ".join(map(str, run_log.get("path_history", [])))
        success = run_log.get("success", False)
        final_outcome = "SUCCESS" if success else "FAILURE"
        final_command = "OSTENDO 'NAVIGATOR'" if success else "REDIMO 'NAVIGATOR'"

        return (
            f"You are a system that converts agent logs into AetherOS story commands.\n"
            f"Your output MUST be a valid JSON array of strings and nothing else.\n\n"
            f"--- EXAMPLE OF A GOOD, CORRECT OUTPUT ---\n"
            f"Input Log:\n- Path: (0, 0) -> (1, 1)\n- Outcome: SUCCESS\n"
            f"Correct Output:\n"
            f"[\n"
            f"  \"CREO 'NAVIGATOR'\",\n"
            f"  \"PERTURBO 'A journey begins.'\",\n"
            f"  \"PERTURBO 'It moves to (1, 1) and finds the goal.'\",\n"
            f'  "{final_command}",\n'
            f'  "vale"\n'
            f"]\n\n"
            f"--- YOUR TASK ---\n"
            f"Convert the following log into the correct JSON array format.\n"
            f"Input Log:\n- Path: {path_string}\n- Outcome: {final_outcome}\n"
            f"Correct Output:"
        )

    async def generate(self, run_log, output_filename):
        """Generates and saves the Saga JSON file."""
        if not self.player:
            print("--- ERROR: SagaGenerator player not initialized. Aborting. ---")
            return False

        print(
            f"\nGenerating Saga using {self.player.model_name}, saving to {output_filename}..."
        )
        prompt = self._build_prompt(run_log)

        try:
            async with aiohttp.ClientSession() as session:
                response_text = await self.player.get_response(prompt, session)

            # Clean the response to find the JSON array
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError(
                    f"No valid JSON array found in LLM response. Response was: {response_text}"
                )

            clean_response = response_text[json_start:json_end]
            story_commands = json.loads(clean_response)

            with open(output_filename, "w") as f:
                json.dump(story_commands, f, indent=2)

            print(f"Saga successfully generated and saved.")
            return True
        except Exception as e:
            print(f"--- ERROR: Failed to generate or parse Saga: {e} ---")
            return False


async def main():
    parser = argparse.ArgumentParser(
        description="Generate a narrative Saga from a mock log."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Key for the model from model_registry.json.",
    )
    args = parser.parse_args()
    mock_run_log = {
        "path_history": [(0, 0), (1, 1), (2, 2)],
        "success": True,
    }
    saga_gen = SagaGenerator(model_key=args.model)
    if saga_gen.player:
        await saga_gen.generate(mock_run_log, "saga_run_0.json")


if __name__ == "__main__":
    asyncio.run(main())
