# sagas/saga_generator.py (Updated with Retry Logic)

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
            print(f"SagaGenerator initialized with player for model: {self.player.model_name}")

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
            
    def _build_prompt(self, run_log, is_retry=False):
        """Builds a detailed and 'hardened' prompt to ensure valid JSON output."""
        path_string = " -> ".join(map(str, run_log.get("path_history", [])))
        success = run_log.get("success", False)
        final_outcome = "SUCCESS" if success else "FAILURE"
        
        retry_message = "\nIMPORTANT: Your previous attempt failed to produce valid JSON. You MUST respond with only a valid JSON array of strings." if is_retry else ""

        return (
            f"You are a system that converts agent logs into AetherOS story commands.\n"
            f"Your output MUST be a valid JSON array of strings and nothing else.{retry_message}\n\n"
            f"--- EXAMPLE OF A GOOD, CORRECT OUTPUT ---\n"
            f"Input Log:\n- Path: (0, 0) -> (1, 1)\n- Outcome: SUCCESS\n"
            f"Correct Output:\n"
            f"[\n"
            f"  \"CREO 'NAVIGATOR'\",\n"
            f"  \"PERTURBO 'A journey begins.'\",\n"
            f"  \"OSTENDO 'NAVIGATOR'\",\n"
            f"  \"vale\"\n"
            f"]\n\n"
            f"--- YOUR TASK ---\n"
            f"Convert the following log into the correct JSON array format.\n"
            f"Input Log:\n- Path: {path_string}\n- Outcome: {final_outcome}\n"
            f"Correct Output:"
        )

    async def generate(self, run_log, output_filename, max_retries=2):
        """Generates and saves the Saga JSON file with a retry loop."""
        if not self.player:
            print("--- ERROR: SagaGenerator player not initialized. Aborting. ---")
            return False

        print(f"\nGenerating Saga using {self.player.model_name}, saving to {output_filename}...")
        
        for attempt in range(max_retries + 1):
            try:
                prompt = self._build_prompt(run_log, is_retry=(attempt > 0))
                
                async with aiohttp.ClientSession() as session:
                    response_text = await self.player.get_response(prompt, session)

                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError("No valid JSON array found in the LLM response.")
                
                clean_response = response_text[json_start:json_end]
                story_commands = json.loads(clean_response)

                with open(output_filename, "w") as f:
                    json.dump(story_commands, f, indent=2)

                print(f"Saga successfully generated and saved.")
                return True # Success, exit the loop
            
            except Exception as e:
                print(f"--- Attempt {attempt + 1} failed: {e} ---")
                if attempt >= max_retries:
                    print("--- ERROR: Max retries reached. Failed to generate Saga. ---")
                    # Create an empty file to prevent crashes
                    with open(output_filename, "w") as f:
                        json.dump(["CREO 'FAILED_SAGA'"], f)
                    return False
                await asyncio.sleep(1) # Wait a second before retrying
