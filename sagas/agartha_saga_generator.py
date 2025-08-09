import json
import asyncio
import aiohttp
import argparse
from experiri.model_loader import load_player
import re

class AgarthaSagaGenerator:
    """Generates narrative Sagas from Agartha story chunks using a schema."""
    def __init__(self, model_key=None):
        if model_key:
            self.player = load_player(model_key)
        else:
            self.player = self.prompt_for_player()
        if self.player:
            print(f"AgarthaSagaGenerator initialized with player for model: {self.player.model_name}")
    
    def prompt_for_player(self):
        print("\n--- Model Selection for Agartha Saga Generation ---")
        try:
            with open("models/model_registry.json", "r") as f:
                registry = json.load(f)
            llm_keys = [k for k, v in registry.items() if v.get('type') != 'hrm']
            print("Available models:")
            for i, key in enumerate(llm_keys):
                print(f" {i+1}: {key}")
            while True:
                choice = input(f"Select a model by number (1-{len(llm_keys)}): ")
                if choice.isdigit() and 1 <= int(choice) <= len(llm_keys):
                    return load_player(llm_keys[int(choice) - 1])
                else:
                    print("Invalid selection. Please try again.")
        except Exception as e:
            print(f"Could not load models from registry: {e}")
            return None
    
    def _build_prompt(self, chunk, schema):
        """Builds a prompt for Agartha-themed sagas ensuring valid JSON output."""
        schema_str = json.dumps(schema, indent=2)
        return (
            f"You are a system that converts Agartha narrative chunks into AetherOS story commands, guided by this schema: {schema_str}.\n"
            f"Your output MUST be a valid JSON array of strings and nothing else.\n\n"
            f"--- EXAMPLE OF A GOOD, CORRECT OUTPUT ---\n"
            f"Input Chunk: ...description of subterranean kingdom...\n"
            f"Correct Output:\n"
            f"[\n"
            f" \"CREO 'KING_OF_THE_WORLD'\",\n"
            f" \"PERTURBO 'The King prays in the subterranean palace.'\",\n"
            f" \"DOCEO 'Mystery of Agharti revealed.'\",\n"
            f" \"OSTENDO 'AGHARTI'\",\n"
            f" \"vale\"\n"
            f"]\n\n"
            f"--- YOUR TASK ---\n"
            f"Convert the following chunk into the correct JSON array format, incorporating schema elements like characters, locations, and themes from Agartha.\n"
            f"Input Chunk:\n{chunk}\n"
            f"Correct Output:"
        )
    
    async def generate(self, chunk, schema, base_filename, chunk_index, max_retries=3):
        """Generates and saves Saga JSON for a chunk."""
        if not self.player:
            print("--- ERROR: AgarthaSagaGenerator player not initialized. Aborting. ---")
            return False
        
        print(f"\nGenerating Saga chunk {chunk_index} using {self.player.model_name}, saving to {base_filename}_{chunk_index}.json...")
        prompt = self._build_prompt(chunk, schema)
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    response_text = await self.player.get_response(prompt, session)
                json_start = response_text.find("[")
                json_end = response_text.rfind("]") + 1
                if json_start == -1 or json_end == 0:
                    raise ValueError(f"No valid JSON array found in response: {response_text}")
                clean_response = response_text[json_start:json_end]
                story_commands = json.loads(clean_response)
                output_filename = f"{base_filename}_{chunk_index}.json"
                with open(output_filename, "w") as f:
                    json.dump(story_commands, f, indent=2)
                print(f"Saga chunk {chunk_index} successfully generated and saved.")
                return True
            except Exception as e:
                print(f"--- Attempt {attempt + 1}/{max_retries} failed: {e} ---")
                if attempt < max_retries - 1:
                    prompt += "\n\nPrevious output was invalid JSON. Fix it and output valid JSON only."
                else:
                    print(f"--- ERROR: Failed to generate Saga chunk {chunk_index} after {max_retries} attempts ---")
                    return False
    
    def split_text(self, text, group_size=2000):
        """Splits the text into chunks based on character count."""
        chunks = [text[i:i + group_size] for i in range(0, len(text), group_size)]
        return chunks

async def main():
    parser = argparse.ArgumentParser(description="Generate Agartha Sagas from narrative text using schema.")
    parser.add_argument("--input_file", help="Path to file containing narrative text.")
    parser.add_argument("--schema_file", help="Path to schema JSON file.")
    parser.add_argument("--model", type=str, default=None, help="Key for the model from model_registry.json.")
    parser.add_argument("--output_base", default="agartha_saga", help="Base filename for output JSON files (will append _i.json).")
    parser.add_argument("--group_size", type=int, default=2000, help="Character count per Saga chunk.")
    args = parser.parse_args()
    
    if args.input_file and args.schema_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
        with open(args.schema_file, 'r') as f:
            schema = json.load(f)
    else:
        print("Error: Provide --input_file and --schema_file.")
        return
    
    agartha_saga_gen = AgarthaSagaGenerator(model_key=args.model)
    if agartha_saga_gen.player:
        chunks = agartha_saga_gen.split_text(text, args.group_size)
        print(f"Split narrative into {len(chunks)} chunks.")
        for i, chunk in enumerate(chunks):
            await agartha_saga_gen.generate(chunk, schema, args.output_base, i)

if __name__ == "__main__":
    asyncio.run(main())
