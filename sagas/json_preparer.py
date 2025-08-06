# sagas/json_preparer.py
# Prepares structured JSON from plaintext using a model from the central registry.

import json
import argparse
import asyncio
import aiohttp
from experiri.model_loader import load_player

# --- THIS FUNCTION IS UNCHANGED ---
def build_prompt(text, schema):
    if schema == "dict":
        return f"""Analyze the following narrative text: {text}. Extract and structure it into a JSON object with these exact keys:
'story' (a string title),
'setting' (an object with 'location' string, 'colors' array of strings, 'atmosphere' string),
'characters' (an object with sub-objects for each main character like 'ADAM' and 'EVE', each containing 'state' string, 'features' array, 'emotions' array, 'actions' array),
'narrative' (a concise summary string incorporating key events, dialogues, and AetherOS concepts like PERTURBO or Scarlet Thread),
'contextus' (an object with 'last_input' string, 'oraculum_responsum' string, 'inter_echo' string, 'fluxum' number).
Ensure the output is valid JSON only—no additional text."""
    elif schema == "commands":
        return f"""Convert the following narrative text into a sequence of AetherOS commands as a JSON array of strings: {text}.
Map elements like character introductions to 'CREO', descriptions
or events to 'PERTURBO', focuses to 'FOCUS', teachings to 'DOCEO', dialectics to 'DIALECTICA', redemptions to 'REDIMO', interrogations to 'INTERROGO', love boosts to 'AMOR', and end with 'OSTENDO' and 'vale'.
Incorporate story-specific details (e.g., names, emotions, actions) into the command arguments. Output only the JSON array."""
    else:
        raise ValueError("Invalid schema. Use 'dict' or 'commands'.")

# --- THIS FUNCTION IS REFACTORED FOR ASYNC AND PROTOCOL ---
async def get_json_from_llm(prompt, player, max_retries=3):
    """
    Asynchronously queries an LLM player and retries if the response is not valid JSON.
    """
    for attempt in range(max_retries):
        print(f"Querying {player.model_name}... (Attempt {attempt + 1}/{max_retries})")
        async with aiohttp.ClientSession() as session:
            # All players return a consistent, parsed Python dictionary.
            response_data = await player.get_response(prompt, session)

        if response_data and "error" not in response_data:
            return response_data
        
        print(f"  > Received invalid or error response: {response_data}")
        # The retry prompt is added here as it's part of the retry logic, not the base prompt.
        prompt += "\n\nPrevious output was invalid JSON. Fix it and output valid JSON only."
    
    raise ValueError("Failed to get valid JSON after multiple retries.")

# --- THIS FUNCTION IS NEW - HANDLES THE GRACEFUL PROMPT ---
def get_player_interactively(model_key=None):
    """Loads a player from a key, or prompts the user if no key is given."""
    if model_key:
        return load_player(model_key)
    
    print("\n--- Model Selection for JSON Preparation ---")
    try:
        with open('models/model_registry.json', 'r') as f:
            registry = json.load(f)
        
        print("Available models:")
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

# --- THIS IS THE MAIN LOGIC, NOW ASYNC ---
async def main():
    parser = argparse.ArgumentParser(description="Prepare JSON from plaintext for AetherOS story_runner.py.")
    parser.add_argument("--text", help="The plaintext narrative (or use --input_file).")
    parser.add_argument("--input_file", help="Path to file containing plaintext narrative.")
    # The default for schema remains "commands" as in the original script.
    parser.add_argument("--schema", choices=["dict", "commands"], default="commands", help="JSON schema type.")
    # The default for model is now None, which triggers the interactive prompt.
    parser.add_argument("--model", default=None, help="Model key from model_registry.json. If omitted, will prompt.")
    parser.add_argument("--output", default="story.json", help="Output JSON file path.")
    args = parser.parse_args()

    # Load text from file or argument
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("Error: Provide either --text or --input_file.")
        return

    try:
        # Gracefully load the player, either from args or by prompting
        player = get_player_interactively(args.model)
        if not player:
            print("No player loaded. Exiting.")
            return

        prompt = build_prompt(text, args.schema)
        json_data = await get_json_from_llm(prompt, player)

        with open(args.output, 'w') as f:
            json.dump(json_data, f, indent=4)
        
        print(f"\nSuccess! JSON prepared and saved to {args.output}.")

    except (ValueError, FileNotFoundError, NotImplementedError) as e:
        print(f"\n--- An error occurred: {e} ---")

if __name__ == "__main__":
    asyncio.run(main())
