import json
import argparse
import asyncio
import aiohttp
from experiri.model_loader import load_player
import re

def build_schema_prompt(text):
    return f"""Analyze the following narrative text from the Mystery of Mysteries: {text}.
Extract and structure persistent components into a JSON object with these exact keys:
'characters' (an object with sub-objects for each main character, e.g., 'King of the World': {{'description': string, 'associations': array of strings, 'emotions': array of strings, 'goals': array of strings}}),
'locations' (an array of objects, each with 'name': string, 'description': string, 'associations': array of strings),
'environments' (an array of strings describing overall settings like 'subterranean passages' or 'limitless plains'),
'associations' (an object mapping relationships, e.g., 'King of the World to Agharti': 'ruler'),
'emotions' (an array of prevalent emotions in the narrative, e.g., ['fear', 'mystery']),
'goals' (an array of main narrative goals or themes, e.g., ['search for the King of the World', 'prophecy fulfillment']).
Ensure the output is valid JSON only—no additional text."""

async def get_json_from_llm(prompt, player, max_retries=3):
    for attempt in range(max_retries):
        print(f"Querying {player.model_name}... (Attempt {attempt + 1}/{max_retries})")
        async with aiohttp.ClientSession() as session:
            response_data = await player.get_response(prompt, session)
        if response_data and "error" not in response_data:
            return response_data
        print(f" > Received invalid or error response: {response_data}")
        prompt += "\n\nPrevious output was invalid JSON. Fix it and output valid JSON only."
    raise ValueError("Failed to get valid JSON after multiple retries.")

def get_player_interactively(model_key=None):
    if model_key:
        return load_player(model_key)
    print("\n--- Model Selection for Schema Generation ---")
    try:
        with open('models/model_registry.json', 'r') as f:
            registry = json.load(f)
        print("Available models:")
        llm_keys = [k for k, v in registry.items() if v.get('type') != 'hrm']
        for i, key in enumerate(llm_keys):
            print(f" {i+1}: {key}")
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

def split_text(text, group_size=2000):
    """Splits the text into chunks based on character count for large narratives."""
    chunks = [text[i:i + group_size] for i in range(0, len(text), group_size)]
    return chunks

async def main():
    parser = argparse.ArgumentParser(description="Generate schema from Agartha narrative text.")
    parser.add_argument("--input_file", help="Path to file containing narrative text.")
    parser.add_argument("--model", default=None, help="Model key from model_registry.json. If omitted, will prompt.")
    parser.add_argument("--output", default="agartha_schema.json", help="Output JSON file path.")
    parser.add_argument("--group_size", type=int, default=2000, help="Character count per chunk.")
    args = parser.parse_args()
    
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    else:
        print("Error: Provide --input_file.")
        return
    
    try:
        player = get_player_interactively(args.model)
        if not player:
            print("No player loaded. Exiting.")
            return
        
        chunks = split_text(text, args.group_size)
        print(f"Split narrative into {len(chunks)} chunks.")
        
        all_schema = {}
        for i, chunk in enumerate(chunks):
            prompt = build_schema_prompt(chunk)
            json_data = await get_json_from_llm(prompt, player)
            # Merge schemas from chunks (simple union for demo; refine as needed)
            for key in json_data:
                if key in all_schema:
                    if isinstance(all_schema[key], list):
                        all_schema[key].extend(json_data[key])
                    elif isinstance(all_schema[key], dict):
                        all_schema[key].update(json_data[key])
                else:
                    all_schema[key] = json_data[key]
        
        with open(args.output, 'w') as f:
            json.dump(all_schema, f, indent=4)
        
        print(f"Schema processed and saved to {args.output}.")
    except (ValueError, FileNotFoundError, NotImplementedError) as e:
        print(f"\n--- An error occurred: {e} ---")

if __name__ == "__main__":
    asyncio.run(main())
