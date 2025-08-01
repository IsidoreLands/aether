import subprocess
import json
import argparse
import os
import sys
import re

# Reuse the run function from story_runner.py (import it)
from story_runner import run_story_from_file  # Assuming story_runner.py is in the same dir

def load_commands_from_file(story_filepath):
    """Load commands from a JSON file, similar to story_runner.py but without running."""
    if not os.path.exists(story_filepath):
        print(f"ERROR: Story file not found at '{story_filepath}'")
        sys.exit(1)
    
    try:
        with open(story_filepath, 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        
        if isinstance(story_data, dict) and "commands" in story_data:
            return story_data["commands"]
        elif isinstance(story_data, list):
            return story_data
        else:
            print("ERROR: The JSON file must contain a list of command strings or an object with a 'commands' key.")
            sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse the JSON file '{story_filepath}'. Please check for syntax errors.")
        sys.exit(1)

def filter_duplicate_creo(commands, created):
    """Filter out CREO commands for already created Materiae."""
    filtered = []
    for cmd in commands:
        match = re.match(r"CREO\s+'([^']+)'", cmd.upper())
        if match:
            name = match.group(1)
            if name in created:
                continue  # Skip duplicate CREO
            created.add(name)
        filtered.append(cmd)
    return filtered

def run_multi_stories(story_filepaths, os_script_name):
    if not os.path.exists(os_script_name):
        print(f"ERROR: The specified OS file '{os_script_name}' does not exist.")
        return

    all_commands = []
    created_materiae = set()  # Track created names across stories

    for filepath in story_filepaths:
        print(f"--- Loading story from '{os.path.basename(filepath)}' ---")
        commands = load_commands_from_file(filepath)
        # Remove any "vale" from all stories (ignored in chaining)
        commands = [cmd for cmd in commands if cmd.strip().lower() != "vale"]
        # Filter duplicate CREO
        commands = filter_duplicate_creo(commands, created_materiae)
        all_commands.extend(commands)

    # Add a single "vale" at the very end to exit the REPL cleanly
    all_commands.append("vale")

    command_script = "\n".join(all_commands)

    print(f"Feeding chained commands to '{os_script_name}' REPL...")
    print("-" * 50)
    
    try:
        process = subprocess.Popen(
            ['python', os_script_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=command_script, timeout=600)
        
        print(stdout)
        
        if stderr:
            print("\n--- Errors Reported by Subprocess ---")
            print(stderr)
            
    except FileNotFoundError:
        print("ERROR: 'python' command not found. Make sure Python is in your system's PATH.")
    except subprocess.TimeoutExpired:
        print("\n--- ERROR: The chained stories took too long to run and timed out. ---")

    print("-" * 50)
    print("--- Chained Stories Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multiple stories through AetherOS in one session.")
    parser.add_argument("story_files", nargs="+", help="Paths to the story JSON files (in order).")
    parser.add_argument("--os", default="aether_os.py", help="The AetherOS script to run (e.g., 'aether_os.py').")
    args = parser.parse_args()
    
    run_multi_stories(args.story_files, args.os)