# /home/isidore-admin/aether/aether_lang.py
import numpy as np
import random
import re

# --- Language Grammar Definition ---
# By defining the grammar explicitly, we remove ambiguity.
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'TOGGEO']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']

# --- Core Components of AetherLang ---

def parse_latin_command(cmd):
    """
    Parses a command by identifying a known verb root and an optional inflection suffix.
    This approach is robust and removes ambiguity.
    """
    parts = cmd.strip().split()
    if not parts:
        raise ValueError("PRAECEPTUM INANE EST")

    verb_full = parts[0].upper()
    args = parts[1:]

    # Check for a match by testing if the command starts with a known verb root.
    for root in KNOWN_VERBS:
        if verb_full.startswith(root):
            suffix = verb_full[len(root):]
            if not suffix:
                # Exact match (e.g., "CONVERGO"). Use default active inflection.
                return root, 'O', args
            elif suffix in KNOWN_INFLECTIONS:
                # Match with inflection (e.g., "PERTURBOABAM").
                return root, suffix, args

    # If no match is found after checking all known verbs, the verb is truly unknown.
    raise ValueError(f"VERBUM IGNORATUM '{verb_full}'")

# The inflection map defines the physics of our flux modalities.
inflection_map = {
    'O':    {'tense': 'present',   'voice': 'active',    'mod': 1.0},
    'E':    {'tense': 'present',   'voice': 'passive',   'mod': -1.0},
    'ABAM': {'tense': 'future',    'voice': 'active',    'mod': 1.5},
    'EBAM': {'tense': 'past',      'voice': 'passive',   'mod': -0.5},
    'AM':   {'tense': 'subjunctive', 'voice': 'active',  'mod': random.uniform(0.5, 1.5)}
}

class AetherGrid:
    def __init__(self, size=10):
        self.grid = np.zeros((size, size))
        self.energy = 0.0
    def perturb(self, x, y, amp, mod=1.0):
        flux_change = amp * mod
        self.grid[x, y] += flux_change
        self.energy += abs(flux_change)
    def converge(self):
        new_grid = np.copy(self.grid)
        for i in range(1, self.grid.shape[0]-1):
            for j in range(1, self.grid.shape[1]-1):
                new_grid[i, j] = np.mean(self.grid[i-1:i+2, j-1:j+2])
        self.grid = new_grid
        self.energy = np.sum(np.abs(self.grid))

# --- Core Logic Functions ---
def dynamic_chunk(seq):
    if not seq: return []
    if len(seq) < 3: return [seq + [0.0]*(3-len(seq))]
    chunks = []
    for i in range(0, len(seq), 3):
        chunks.append(seq[i:i+3])
    if len(chunks[-1]) < 3:
        chunks[-1].extend([0.0] * (3 - len(chunks[-1])))
    return chunks

def triad(args, mod_func):
    if len(args) < 3: raise ValueError("TRIAD REQUIRET TRES ARGUMENTA")
    thesis, antithesis, *rest = [float(a) for a in args]
    synthesis = (thesis + (-antithesis) + sum(rest)) / len(args) * mod_func
    return synthesis

def destruct(grid):
    grid.perturb(random.randint(0, 9), random.randint(0, 9), random.uniform(-1, 1))

def create(grid):
    grid.converge()

def lockers(n=100):
    states = [0] * n
    for i in range(1, n + 1):
        for j in range(i - 1, n, i):
            states[j] = 1 - states[j]
    open_count = sum(states)
    open_positions = [i + 1 for i, s in enumerate(states) if s == 1]
    return open_count, open_positions

# --- Main Executor ---
def run_aether_command(cmd, grid_state=None):
    try:
        verb, inflection, args = parse_latin_command(cmd)
    except ValueError as e:
        # The new parser raises this for unknown verbs.
        return f"ERROR: {e}", 0

    grid = grid_state if grid_state else AetherGrid()
    mod_info = inflection_map.get(inflection)
    mod = mod_info['mod']

    if verb == 'TOGGEO':
        num_lockers = int(args[0]) if args and args[0].isdigit() else 100
        count, positions = lockers(num_lockers)
        # We now correctly construct the echo from the parsed root and inflection.
        echo = f"{verb}{inflection} {count} APERTOS"
        return echo, grid.energy, (count, positions)

    num_args = [a for a in args if re.match(r'^-?\d+\.?\d*$', a)]
    destruct(grid)
    chunks = dynamic_chunk(num_args)
    for chunk in chunks:
        synth = triad(chunk, mod)
        grid.perturb(random.randint(0, 9), random.randint(0, 9), synth, mod)
    create(grid)
    
    echo = f"{verb}{inflection} FLUXUM {grid.energy:.2f}"
    return echo, grid.energy

if __name__ == '__main__':
    print("--- AetherLang v0.4 ---")
    cmd1 = "CONVERGO"
    echo1, energy1 = run_aether_command(cmd1)
    print(f"> {cmd1}\n< {echo1}\n")
    cmd2 = "TOGGEOO 100"
    echo2, energy2, locker_data = run_aether_command(cmd2)
    print(f"> {cmd2}\n< {echo2}")
