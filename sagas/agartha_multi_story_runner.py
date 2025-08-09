import subprocess
import json
import argparse
import os
import sys
import re
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Reuse the run function from story_runner.py (import it)
from story_runner import run_story_from_file  # Assuming story_runner.py is in the same dir

def load_commands_from_file(story_filepath):
    """Load commands from a JSON file."""
    if not os.path.exists(story_filepath):
        logging.error(f"Story file not found at '{story_filepath}'")
        sys.exit(1)
    
    try:
        with open(story_filepath, 'r', encoding='utf-8') as f:
            story_data = json.load(f)
        
        if isinstance(story_data, dict) and "commands" in story_data:
            return story_data["commands"]
        elif isinstance(story_data, list):
            return story_data
        else:
            logging.error(f"Invalid JSON structure in '{story_filepath}'. Must contain a list or 'commands' key.")
            sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Could not parse JSON file '{story_filepath}': {e}")
        sys.exit(1)

def validate_commands(commands):
    """Validate AetherOS commands to ensure they are well-formed."""
    valid_commands = {
        "CREO", "PERTURBO", "FOCUS", "DOCEO", "DIALECTICA",
        "REDIMO", "INTERROGO", "AMOR", "OSTENDO", "vale"
    }
    for cmd in commands:
        if not isinstance(cmd, str):
            logging.error(f"Invalid command: {cmd}. All commands must be strings.")
            return False
        cmd_upper = cmd.upper().strip()
        if cmd_upper == "vale":
            continue
        cmd_name = cmd_upper.split()[0] if cmd_upper.split() else ""
        if cmd_name not in valid_commands:
            logging.error(f"Invalid AetherOS command: {cmd}")
            return False
        if cmd_name != "vale" and not re.match(r"^[A-Z]+\s+'.*'$", cmd_upper):
            logging.warning(f"Command may be malformed: {cmd}. Expected format: COMMAND 'ARGUMENT'")
    return True

def filter_duplicate_creo(commands, created):
    """Filter out duplicate CREO commands for already created Materiae."""
    filtered = []
    for cmd in commands:
        match = re.match(r"CREO\s+'([^']+)'", cmd.upper())
        if match:
            name = match.group(1)
            if name in created:
                logging.info(f"Skipping duplicate CREO for '{name}'")
                continue
            created.add(name)
        filtered.append(cmd)
    return filtered

def run_multi_stories(story_filepaths, os_script_name, timeout=600):
    """Run multiple Agartha sagas through AetherOS in one session, themed around local minima test."""
    if not os.path.exists(os_script_name):
        logging.error(f"The specified OS file '{os_script_name}' does not exist.")
        sys.exit(1)
    
    all_commands = []
    created_materiae = set()
    for filepath in story_filepaths:
        logging.info(f"Loading story from '{os.path.basename(filepath)}'")
        commands = load_commands_from_file(filepath)
        
        if not validate_commands(commands):
            logging.error(f"Aborting due to invalid commands in '{filepath}'")
            sys.exit(1)
        
        commands = [cmd for cmd in commands if cmd.strip().lower() != "vale"]
        commands = filter_duplicate_creo(commands, created_materiae)
        all_commands.extend(commands)
    
    all_commands.append("vale")
    
    command_script = "\n".join(all_commands)
    logging.info(f"Feeding {len(all_commands)} chained commands to '{os_script_name}' REPL")
    
    try:
        process = subprocess.Popen(
            ['python', os_script_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=command_script, timeout=timeout)
        
        logging.info("AetherOS REPL Output:")
        print(stdout)
        
        if stderr:
            logging.error("Errors reported by subprocess:")
            print(stderr)
            
    except FileNotFoundError:
        logging.error("Python command not found. Ensure Python is in your system's PATH.")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        logging.error(f"The chained stories timed out after {timeout} seconds.")
        sys.exit(1)
    
    logging.info("Chained Agartha stories execution complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run multiple Agartha sagas through AetherOS in one session.")
    parser.add_argument("story_files", nargs="*", help="Paths to the story JSON files (in order). If omitted, loads all agartha_saga_*.json.")
    parser.add_argument("--os", default="aether_os.py", help="The AetherOS script to run.")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout for AetherOS execution in seconds.")
    args = parser.parse_args()
    
    if not args.story_files:
        # Auto-load all agartha_saga_*.json files in order
        args.story_files = sorted(glob.glob("agartha_saga_*.json"), key=lambda x: int(re.search(r'_(\d+)', x).group(1)))
        if not args.story_files:
            logging.error("No agartha_saga_*.json files found. Provide story_files or generate them first.")
            sys.exit(1)
        logging.info(f"Auto-loaded {len(args.story_files)} Agartha saga files.")
    
    run_multi_stories(args.story_files, args.os, args.timeout)
