# sagas/saga_generator.py
# This module generates a narrative Saga from a test run log using a
# model from the central registry.

import json
import asyncio
import aiohttp
import argparse
from experiri.model_loader import load_player

class SagaGenerator:
    """Generates a narrative Saga from a test run log."""

    def __init__(self, model_key=None):
        """
        Initializes the generator. If no model_key is provided, it will
        prompt the user to select one.
        """
        if model_key:
            self.player = load_player(model_key)
        else:
            self.player = self.prompt_for_player()
        
        if self.player:
            print(f"SagaGenerator initialized with player for model: {self.player.model_name}")

    def prompt_for_player(self):
        """Prompts the user to select a model if none was specified via arguments."""
        print("\n--- Model Selection for Saga Generation ---")
        try:
            with open('models/model_registry.json', 'r') as f:
                registry = json.load(f)
            
            print("Available models:")
            # We only want to list LLMs, not specialized models like the HRM
            llm_keys = [k for k, v in registry.items() if v.get('type') != 'hrm']
            for i, key in enumerate(llm_keys):
                print(f"  {i+1}: {key}")
            
            while True:
                choice = input(f"Select a model by number (1-{len(llm_keys)}): ")
                if choice.isdigit() and 1 <= int(choice) <= len(llm_keys):
                    selected_key = llm_keys[int(choice) - 1]
                    return load_player(selected_key)
                else:
                    print("Invalid selection. Please try again.")
        except Exception as e:
            print(f"Could not load models from registry: {e}")
            return None

    def _build_prompt(self, run_log):
        """Builds a detailed prompt for the LLM to generate the Saga."""
        path_string = " -> ".join(map(str, run_log.get('path_history', [])))
        success = run_log.get('success', False)
        final_outcome = "SUCCESS" if success else "FAILURE (stuck in a loop)"

        return (
            f"Analyze the following log from an AI agent's maze attempt from (0, 0) to (10, 10).\n"
            f"- Path: {path_string}\n- Outcome: {final_outcome}\n\n"
            f"Your task is to convert this into a brief, allegorical story as a JSON array of AetherOS commands.\n"
            f"- Agent is 'NAVIGATOR'. Use PERTURBO for journey points. End with REDIMO on failure or OSTENDO on success. "
            f"Conclude with a 'vale' command.\n\n"
            f"IMPORTANT: Respond with only the valid JSON array of strings. Do not include any other text, explanations, or markdown."
        )

    async def generate(self, run_log, output_filename):
        """Generates and saves the Saga JSON file."""
        if not self.player:
            print("--- ERROR: SagaGenerator player not initialized. Aborting. ---")
            return False
        
        print(f"\nGenerating Saga using {self.player.model_name}, saving to {output_filename}...")
        prompt = self._build_prompt(run_log)

        try:
            async with aiohttp.ClientSession() as session:
                # All player types now return a consistent, parsed Python dictionary.
                # The SagaGenerator is now completely agnostic of the model source.
                story_commands = await self.player.get_response(prompt, session)

            if isinstance(story_commands, dict) and "error" in story_commands:
                raise ValueError(story_commands["error"])

            with open(output_filename, 'w') as f:
                json.dump(story_commands, f, indent=2)
            
            print(f"Saga successfully generated and saved.")
            return True
        except Exception as e:
            print(f"--- ERROR: Failed to generate or parse Saga: {e} ---")
            return False

async def main():
    """Sets up and runs the SagaGenerator."""
    parser = argparse.ArgumentParser(description="Generate a narrative Saga from a mock log.")
    parser.add_argument('--model', type=str, default=None,
                        help="Key for the model from model_registry.json (e.g., ollama_phi3). If not provided, will prompt.")
    
    args = parser.parse_args()

    mock_run_log = {
        'path_history': [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (4, 3), (4, 2)], 
        'success': False
    }
    
    # Instantiate with a key from arguments, or let it prompt the user
    saga_gen = SagaGenerator(model_key=args.model)
    if saga_gen.player:
        await saga_gen.generate(mock_run_log, "saga_run_0.json")

if __name__ == '__main__':
    asyncio.run(main())
