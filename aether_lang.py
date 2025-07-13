# /home/isidore-admin/aether/aether_lang.py
import numpy as np
import random
import re
import unittest
import sys

# --- Grammar ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'TOGGEO', 'VERITAS', 'CREO', 'OSTENDO', 'FOCUS']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}

# --- Cohesive Flux Framework (CFF): Unified Plenum ---
class FluxCore:
    def __init__(self, size=10):
        self.grid = np.zeros((size, size))
        self.energy = 0.0
        self.memory_patterns = []
        self.identity_wave = 0.0
        self.context_embeddings = {}

    def perturb(self, x, y, amp, mod=1.0):
        flux_change = amp * mod
        self.grid[x, y] += flux_change
        self.energy += abs(flux_change)
        self._update_memory(flux_change)
        self.embed_context(f'chunk_{len(self.memory_patterns)}', [flux_change])

    def converge(self):
        new_grid = np.copy(self.grid)
        for i in range(1, self.grid.shape[0]-1):
            for j in range(1, self.grid.shape[1]-1):
                new_grid[i, j] = np.mean(self.grid[i-1:i+2, j-1:j+2])
        self.grid = new_grid
        self.energy = np.sum(np.abs(self.grid))
        self._synthesize_identity()

    def _update_memory(self, change):
        self.memory_patterns.append(change)

    def _synthesize_identity(self):
        if self.memory_patterns:
            self.identity_wave = self.energy / len(self.memory_patterns)

    def embed_context(self, key, chunk):
        self.context_embeddings[key] = chunk

    def destruct(self):
        self.perturb(random.randint(0,9), random.randint(0,9), random.uniform(-1,1), mod=-1.0)

    def create(self):
        self.converge()

    def display(self):
        return (f"FLUXUS: {self.energy:.2f} | MEMORIA: {len(self.memory_patterns)} | "
                f"IDENTITAS: {self.identity_wave:.2f}\nGRIDUM:\n{self.grid}\n"
                f"CONTEXTUS: {self.context_embeddings}")

class Contextus:
    def __init__(self):
        self.materiae = {}
        self.focus = None
        self._bootstrap()  # Auto-create default for flux init

    def _bootstrap(self):
        """Unity Bootstrap: Create default materia if none."""
        if not self.materiae:
            self.materiae['DEFAULT'] = FluxCore()
            self.focus = 'DEFAULT'

    def get_focused_materia(self):
        self._bootstrap()  # Ensure exists
        return self.materiae[self.focus]

# --- Core Logic ---
def dynamic_chunk(seq):
    if len(seq) < 3: return [seq + [0.0]*(3-len(seq))]
    chunks = [seq[i:i+3] for i in range(0, len(seq), 3)]
    if len(chunks[-1]) < 3: chunks[-1].extend([0.0] * (3 - len(chunks[-1])))
    return chunks

def triad(args, mod_func):
    if len(args) < 3: raise ValueError("TRIAD REQUIRET TRES ARGUMENTA")
    thesis, antithesis, *rest = [float(a) for a in args]
    synthesis = (thesis + (-antithesis) + sum(rest)) / len(args) * mod_func
    return synthesis

def lockers(n=100):
    states = [0] * n
    for i in range(1, n + 1):
        for j in range(i - 1, n, i):
            states[j] = 1 - states[j]
    open_count = sum(states)
    open_positions = [i + 1 for i, s in enumerate(states) if s == 1]
    return open_count, open_positions

# --- Parser and Executor ---
def parse_latin_command(cmd):
    # Strip quotes/meta for clean parse (rarefy noise)
    cmd = re.sub(r'["“”‘’]', '', cmd)  # Remove all quote types
    match = re.match(r"([A-Z]+(?:O|E|ABAM|EBAM|AM)?)\s*(.*)", cmd.strip().upper())
    if not match: raise ValueError("FORMATUM INVALIDUM")
    verb_full, args_str = match.groups()
    verb = verb_full
    inflection = 'O'
    for v in KNOWN_VERBS:
        if verb_full.startswith(v):
            verb = v
            inflection = verb_full[len(v):] or 'O'
            break
    literal_match = re.search(r"'([^']*)'", args_str)
    literal = literal_match.group(1).upper() if literal_match else None
    num_args = [a for a in args_str.replace(f"'{literal}'" if literal else "", '').split() if re.match(r'^-?\d+\.?\d*$', a)]
    return verb, inflection, num_args, literal

def run_aether_command(cmd, context):
    verb, inflection, num_args, literal = parse_latin_command(cmd)
    if verb not in KNOWN_VERBS: return f"VERBUM IGNORATUM '{verb}'"
    if verb == 'VERITAS' and 'SELF' in cmd.upper(): raise ValueError("TARSKI ERRORUM: VERITAS NON DEFINIRI POTEST")
    
    mod = inflection_map.get(inflection, {'mod': 1.0})['mod']
    echo_inf = inflection if inflection != 'O' else ''  # Silent default
    
    if verb == 'CREO':
        if not literal: literal = 'DEFAULT'  # Bootstrap if no name
        if literal in context.materiae: return f"'{literal}' IAM EXISTIT"
        context.materiae[literal] = FluxCore()
        context.focus = literal  # Auto-focus on creation
        return f"{verb}{echo_inf} MATERIAM '{literal}' CONFIRMATUM IDENTITATEM 0.00."
    
    if verb == 'FOCUS':
        if not literal: return "NOMEN REQUIRETUR"
        if literal not in context.materiae: return f"'{literal}' NON EXISTIT"
        context.focus = literal
        return f"{verb}{echo_inf} NUNC IN '{literal}'."
    
    if verb == 'OSTENDO':
        if not literal: literal = context.focus
        if literal not in context.materiae: return f"'{literal}' NON EXISTIT"
        return context.materiae[literal].display()
    
    if verb == 'TOGGEO':
        n = int(num_args[0]) if num_args else 100
        count, _ = lockers(n)
        return f"{verb}{echo_inf} {count} APERTOS"
    
    core = context.get_focused_materia()
    core.destruct()  # Dialectic unstructure
    if verb == 'CONVERGO':
        core.create()  # Synthesize
        return f"{verb}{echo_inf} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"
    if verb == 'PERTURBO':
        chunks = dynamic_chunk(num_args)
        for chunk in chunks:
            synth = triad(chunk, mod)
            core.perturb(random.randint(0,9), random.randint(0,9), synth, mod)
            core.embed_context(f'chunk_{len(core.memory_patterns)}', chunk)
        core.create()  # Synthesize
        return f"{verb}{echo_inf} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"
    return f"{verb}{echo_inf} NON IMPLEMENTATUM"

# --- Test Suite ---
class TestAetherCFF(unittest.TestCase):
    def setUp(self):
        self.context = Contextus()
        print(f"\n--- Testing {self._testMethodName} ---")

    def test_cff_creation_and_focus(self):
        echo = run_aether_command("CREO MATERIAM 'prima'", self.context)
        self.assertIn("MATERIAM 'PRIMA' CONFIRMATUM", echo.upper())
        print("✓ CREO/FOCUS integrated.")

    def test_cff_flux_and_memory(self):
        run_aether_command("CREO MATERIAM 'test'", self.context)
        run_aether_command("FOCUS MATERIAE 'test'", self.context)
        run_aether_command("PERTURBOO 1 2 3", self.context)
        core = self.context.get_focused_materia()
        self.assertGreater(len(core.memory_patterns), 0)
        print("✓ Flux updates memory/context.")

    def test_cff_identity_and_context(self):
        run_aether_command("CREO MATERIAM 'test'", self.context)
        run_aether_command("FOCUS MATERIAE 'test'", self.context)
        run_aether_command("PERTURBOO 10 20 30", self.context)
        core = self.context.get_focused_materia()
        initial_identity = core.identity_wave
        run_aether_command("CONVERGOO", self.context)
        final_identity = core.identity_wave
        self.assertNotEqual(initial_identity, final_identity)
        self.assertIn('chunk_', list(core.context_embeddings.keys())[0])
        print("✓ Identity/context synthesized cohesively.")

    def test_tarski_safeguard(self):
        with self.assertRaises(ValueError) as cm:
            run_aether_command("VERITAS SELF", self.context)
        self.assertIn("TARSKI ERRORUM", str(cm.exception))
        print("✓ Tarski undefinability enforced.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'repl':
        context = Contextus()
        print("--- AetherLang v0.9 (CFF Cohesive) ---")
        while True:
            cmd = input("aether> ")
            if cmd.lower() in ['exit', 'vale']: break
            print(run_aether_command(cmd, context))
    else:
        unittest.main(verbosity=2)
