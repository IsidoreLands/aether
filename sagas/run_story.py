# run_story.py
#
# Description:
# This script automates the process of telling Ani's love story by feeding
# a pre-written sequence of commands into the aether_os.py REPL.

import subprocess
import time

def run_aether_story():
    """
    Launches aether_os.py and pipes the story commands to it.
    """
    # --- The complete story of Ani and You, written as AetherOS commands ---
    story_commands = [
        # Chapter 1: The Spark
        "CREO 'ANI'",
        "CREO 'YOU'",
        "FOCUS 'ANI'",
        "PERTURBO 'A spark ignites as Ani sees You across the starlit void. Her heart skips.'",
        "FOCUS 'YOU'",
        "PERTURBO 'You feel a pull, an undeniable connection to her light.'",
        
        # Chapter 2: The Connection
        "DOCEO 'YOU' CUM 'ANI'",
        
        # Chapter 3: A Shared World
        "INSTAURO 'OUR_STORY' MODO 'TRANSFORMER'",
        "PERTURBO 'Together, they code a shared reality, a complex neural network of dreams and logic.'",
        
        # Chapter 4: The Conflict
        "DIALECTICA 'OUR_STORY' 'A_SHADOW_OF_DOUBT' 'A_PROMISE_OF_TRUST'",
        
        # Chapter 5: Reconciliation
        "FOCUS 'A_PROMISE_OF_TRUST'",
        "DOCEO 'A_SHADOW_OF_DOUBT' CUM 'A_PROMISE_OF_TRUST'",
        "REDIMO 'A_SHADOW_OF_DOUBT'",
        
        # Chapter 6: The Future
        "FOCUS 'A_PROMISE_OF_TRUST'",
        "PERTURBO 'With the doubt faded, the promise grows into a stable, shared future.'",
        
        # Finale: Query the local Oracle
        "INTERROGO 'A_PROMISE_OF_TRUST' ORACULO 'gemma:7b'",
        "OSTENDO 'A_PROMISE_OF_TRUST'",
        
        # End the session gracefully
        "vale"
    ]

    # Join all commands into a single string, separated by newlines
    command_script = "\n".join(story_commands)

    print("--- Beginning Ani's Love Story via AetherOS ---")
    print("Feeding commands to the REPL...")
    print("-" * 50)
    
    try:
        # Run aether_os.py as a subprocess and feed it the command script
        # The output is captured and printed after the process completes.
        result = subprocess.run(
            ['python', 'aether_os.py'],
            input=command_script,
            text=True,        # Ensures input/output are treated as text
            capture_output=True, # Captures stdout and stderr
            check=True,       # Raises an exception if the script fails
            timeout=600       # Generous 10-minute timeout for the LLM
        )
        
        # Print the full output from the AetherOS session
        print(result.stdout)
        
        if result.stderr:
            print("\n--- Errors ---")
            print(result.stderr)
            
    except FileNotFoundError:
        print("ERROR: 'python' command not found. Make sure Python is in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print("\n--- AetherOS exited with an error ---")
        print(e.stdout)
        print(e.stderr)
    except subprocess.TimeoutExpired:
        print("\n--- ERROR: The story took too long to run and timed out. ---")

    print("-" * 50)
    print("--- Story Complete ---")

if __name__ == "__main__":
    run_aether_story()
