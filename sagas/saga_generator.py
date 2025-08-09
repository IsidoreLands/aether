# sagas/saga_generator.py
# This module generates an Enriched Saga from a test run log, including
# a summary of guide critiques and a prescriptive SUGGERO command.

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
            print(
                f"SagaGenerator initialized with player for model: {self.player.model_name}"
            )

    def prompt_for_player(self):
        """Prompts the user to select a model if none was specified via arguments."""
        print("\n--- Model Selection for Saga Generation ---")
        try:
            with open("models/model_registry.json", "r") as f:
                registry = json.load(f)

            print("Available models:")
            # We only want to list LLMs, not specialized models like the HRM
            llm_keys = [k for k, v in registry.items() if v.get("type") != "hrm"]
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

    def _build_prompt(self, run_log, guide_critiques, is_retry=False):
        """Builds a prompt for an ENRICHED SAGA, including contrastive feedback."""
        path_string = " -> ".join(map(str, run_log.get("path_history", [])))
        success = run_log.get("success", False)
        final_outcome = "SUCCESS" if success else "FAILURE"
        stuck_position = run_log.get("path_history", [])[-1]
        
        # Synthesize the guide's wisdom into a single string
        critique_summary = " ".join(
            str(critique.get("critique", "")) for critique in guide_critiques if critique
        )

        # Create the specific instruction for the SUGGERO command on failure
        suggero_instruction = (
            (
                "4. CRITICAL: If the outcome was FAILURE, you MUST include a \"SUGGERO 'A better path...'\" command. "
                f"Base this suggestion on the critiques and the fact the agent was stuck at {stuck_position}. For example, if stuck at x=5, suggest moving down or up."
            )
            if not success
            else ""
        )
        
        retry_message = "\nIMPORTANT: Your previous attempt failed to produce valid JSON. You MUST respond with only a valid JSON array of strings." if is_retry else ""

        return (
            f"You are a system that converts agent logs into AetherOS story commands.\n"
            f"Your output MUST be a valid JSON array of strings and nothing else.{retry_message}\n\n"
            f"--- CONTEXTUAL DATA ---\n"
            f"- Path: {path_string}\n- Outcome: {final_outcome}\n- Guide's Critiques Summary: {critique_summary}\n\n"
            f"--- INSTRUCTIONS ---\n"
            f"1. Start with \"CREO 'NAVIGATOR'\".\n"
            f"2. Use 'PERTURBO' to describe the journey.\n"
            f"3. If FAILURE, include a 'PERTURBO' command describing where the agent got stuck.\n"
            f"{suggero_instruction}\n"
            f"5. End with \"REDIMO 'NAVIGATOR'\" on FAILURE, or \"OSTENDO 'NAVIGATOR'\" on SUCCESS.\n"
            f'6. Conclude with "vale".\n\n'
            f"Correct Output:"
        )

    async def generate(self, run_log, guide_critiques, output_filename, max_retries=2):
        """Generates and saves the Saga JSON file with a retry loop."""
        if not self.player:
            print("--- ERROR: SagaGenerator player not initialized. Aborting. ---")
            return False

        print(f"\nGenerating Saga using {self.player.model_name}, saving to {output_filename}...")

        for attempt in range(max_retries + 1):
            try:
                prompt = self._build_prompt(run_log, guide_critiques, is_retry=(attempt > 0))

                async with aiohttp.ClientSession() as session:
                    response_obj = await self.player.get_response(prompt, session)

                story_commands = None
                if isinstance(response_obj, list):
                    story_commands = response_obj
                elif isinstance(response_obj, dict):
                    for key, value in response_obj.items():
                        if isinstance(value, list):
                            story_commands = value
                            print(f"INFO: Extracted command list from key '{key}' in LLM's dictionary response.")
                            break
                
                if story_commands is None:
                    raise ValueError(f"LLM did not return a valid JSON array. Got: {response_obj}")

                with open(output_filename, "w") as f:
                    json.dump(story_commands, f, indent=2)

                print(f"Saga successfully generated and saved.")
                return True

            except Exception as e:
                print(f"--- Attempt {attempt + 1} failed: {e} ---")
                if attempt >= max_retries:
                    print("--- ERROR: Max retries reached. Failed to generate Saga. ---")
                    with open(output_filename, "w") as f:
                        json.dump(["CREO 'FAILED_SAGA'"], f)
                    return False
                await asyncio.sleep(1)

async def main():
    """Sets up and runs the SagaGenerator."""
    parser = argparse.ArgumentParser(
        description="Generate a narrative Saga from a mock log."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Key for the model from model_registry.json (e.g., ollama_phi3). If not provided, will prompt.",
    )

    args = parser.parse_args()

    mock_run_log = {
        "path_history": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
        "success": False,
    }
    mock_critiques = [
        {"critique": "A good start."},
        {"critique": "Seems to be on the right track."},
        {"critique": "This move leads directly into the wall, a poor choice."}
    ]
    
    saga_gen = SagaGenerator(model_key=args.model)
    if saga_gen.player:
        await saga_gen.generate(mock_run_log, mock_critiques, "saga_run_0.json")


if __name__ == "__main__":
    asyncio.run(main())
