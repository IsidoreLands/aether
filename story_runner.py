# story_runner.py
#
# Description:
# This script can run any story defined in a JSON file by feeding its
# commands into a specified AetherOS REPL (standard or Boyd).
# This version has enhanced error reporting.

import subprocess
import json
import argparse
import os

def run_story_from_file(story_filepath, os_script_name):
    """
    Loads a story from a JSON file and pipes the commands to aether_os.py.
    
    Args:
        story_filepath (str): The path to the JSON file containing the story.
        os_script_name (str): The filename of the AetherOS script to run.
    """
    if not os.path.exists(os_script_name):
        print(f"ERROR: The specified OS file '{os_script_name}' does not exist.")
        return

    print(f"--- Loading story from '{os.path.basename(story_filepath)}' ---")
    
    try:
        with open(story_filepath, 'r') as f:
            story_data = json.load(f)
        
        if isinstance(story_data, dict) and "commands" in story_data:
            story_commands = story_data["commands"]
            print(f"--- Running Story: {story_data.get('title', 'Untitled')} ---")
            print(f"--- {story_data.get('description', '')} ---")
        elif isinstance(story_data, list):
            story_commands = story_data
        else:
            print("ERROR: The JSON file must contain a list of command strings or an object with a 'commands' key.")
            return
            
    except FileNotFoundError:
        print(f"ERROR: Story file not found at '{story_filepath}'")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse the JSON file. Please check for syntax errors.")
        return

    command_script = "\n".join(story_commands)

    print(f"Feeding commands to '{os_script_name}' REPL...")
    print("-" * 50)
    
    try:
        # Launch the subprocess
        process = subprocess.Popen(
            ['python', os_script_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the commands and capture the output
        stdout, stderr = process.communicate(input=command_script, timeout=600)
        
        # Print the full output from the AetherOS session
        print(stdout)
        
        # Always print any errors that occurred
        if stderr:
            print("\n--- Errors Reported by Subprocess ---")
            print(stderr)
            
    except FileNotFoundError:
        print("ERROR: 'python' command not found. Make sure Python is in your system's PATH.")
    except subprocess.TimeoutExpired:
        print("\n--- ERROR: The story took too long to run and timed out. ---")

    print("-" * 50)
    print("--- Story Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a story through the AetherOS.")
    parser.add_argument("story_file", help="The path to the story's JSON file.")
    parser.add_argument("--os", default="aether_os.py", help="The AetherOS script to run (e.g., 'aether_os.py' or 'boyd_aether_os.py').")
    args = parser.parse_args()
    
    run_story_from_file(args.story_file, args.os)