# saga_generator.py
#
# This module takes the results of a local_minima_test run and uses an
# LLM to generate a narrative "Saga" in the form of a JSON story file.

import json
from oracle import get_oracle # We reuse our existing oracle to query an LLM

class SagaGenerator:
    """
    Generates a narrative Saga from a test run log.
    """

    def __init__(self, model_name="gemma:7b"):
        """
        Initializes the generator with a specific LLM model.

        Args:
            model_name (str): The name of the LLM to use for generation
                              (e.g., gemma:7b, gemini-1.5-flash).
        """
        self.oracle = get_oracle(model_name)
        print(f"SagaGenerator initialized with oracle: {model_name}")

    def _build_prompt(self, run_log):
        """
        Builds a detailed prompt for the LLM to generate the Saga.
        """
        path_string = " -> ".join(map(str, run_log['path_history']))
        final_outcome = "SUCCESS" if run_log['success'] else "FAILURE (stuck in a loop)"

        prompt = f"""
        Analyze the following log from an AI agent's attempt to solve a maze puzzle.
        The agent's goal was to travel from (0, 0) to (10, 10).

        - Agent's Path: {path_string}
        - Final Outcome: {final_outcome}

        Your task is to convert this journey into a brief, allegorical story formatted as a sequence of AetherOS commands in a JSON array.
        
        - Use "CREO 'NAVIGATOR'" for the agent.
        - Use "PERTURBO" commands to describe key parts of the journey, like starting, getting stuck against the wall (around x=5), or reaching the goal.
        - If the agent failed, end the story with a "REDIMO 'NAVIGATOR'" command to represent its dissolution.
        - If the agent succeeded, end with "OSTENDO 'NAVIGATOR'".
        - Conclude with a "vale" command.
        
        Output only the valid JSON array of strings. Do not include any other text or explanations.
        """
        return prompt

    def generate(self, run_log, output_filename):
        """
        Generates and saves the Saga JSON file.

        Args:
            run_log (dict): A dictionary containing the results of the test run.
                            Expected keys: 'path_history', 'success'.
            output_filename (str): The path to save the generated JSON file.
        """
        print(f"\nGenerating Saga for run, saving to {output_filename}...")
        prompt = self._build_prompt(run_log)

        try:
            # Query the LLM to get the command list
            response_text = self.oracle.query(prompt)
            # The oracle might return the JSON wrapped in markdown, so we extract it.
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start == -1 or json_end == 0:
                raise json.JSONDecodeError("No JSON array found in response.", response_text, 0)
            
            story_commands = json.loads(response_text[json_start:json_end])

            # Save the commands to the output file
            with open(output_filename, 'w') as f:
                json.dump(story_commands, f, indent=2)
            
            print(f"Saga successfully generated and saved.")
            return True

        except (json.JSONDecodeError, Exception) as e:
            print(f"--- ERROR: Failed to generate or parse Saga. ---")
            print(f"Error: {e}")
            return False

# --- Example Usage ---
if __name__ == '__main__':
    # This is mock data representing a failed run where the agent got stuck
    mock_run_log = {
        'path_history': [
            (0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (4, 5), 
            (4, 4), (4, 5), (4, 4) 
        ],
        'success': False
    }

    # Instantiate the generator
    saga_gen = SagaGenerator()

    # Generate the saga file from the mock log
    saga_gen.generate(mock_run_log, "saga_run_0.json")