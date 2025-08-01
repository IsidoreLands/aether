import json
import argparse
import os
from oracle import get_oracle  # Reuse your existing oracle.py

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
Map elements like character introductions to 'CREO', descriptions or events to 'PERTURBO', focuses to 'FOCUS', teachings to 'DOCEO', dialectics to 'DIALECTICA', redemptions to 'REDIMO', interrogations to 'INTERROGO', love boosts to 'AMOR', and end with 'OSTENDO' and 'vale'. 
Incorporate story-specific details (e.g., names, emotions, actions) into the command arguments. Output only the JSON array."""
    else:
        raise ValueError("Invalid schema. Use 'dict' or 'commands'.")

def query_llm(prompt, model, max_retries=3):
    oracle = get_oracle(model)
    for attempt in range(max_retries):
        response = oracle.query(prompt)
        try:
            json_data = json.loads(response)
            return json_data
        except json.JSONDecodeError:
            print(f"Retry {attempt+1}/{max_retries}: Invalid JSON. Response was: {response}")
            prompt += "\nPrevious output was invalid JSON. Fix it and output valid JSON only."
    raise ValueError("Failed to get valid JSON after retries.")

def main():
    parser = argparse.ArgumentParser(description="Prepare JSON from plaintext for AetherOS story_runner.py.")
    parser.add_argument("--text", help="The plaintext narrative (or use --input_file).")
    parser.add_argument("--input_file", help="Path to file containing plaintext narrative.")
    parser.add_argument("--schema", choices=["dict", "commands"], default="commands", help="JSON schema type.")
    parser.add_argument("--model", default="gemma:7b", help="LLM model (e.g., gemma:7b, gemini-1.5-flash).")
    parser.add_argument("--output", default="story.json", help="Output JSON file path.")
    args = parser.parse_args()

    # Load text
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        raise ValueError("Provide --text or --input_file.")

    prompt = build_prompt(text, args.schema)
    json_data = query_llm(prompt, args.model)

    with open(args.output, 'w') as f:
        json.dump(json_data, f, indent=4)
    print(f"JSON prepared and saved to {args.output}. Run with: python story_runner.py {args.output}")

if __name__ == "__main__":
    main()