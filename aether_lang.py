# /home/isidore-admin/aether/aether_lang.py
import numpy as np
import random
import re
import unittest
import sys

# --- Language Grammar Definition ---
KNOWN_VERBS = [
    'PERTURBO', 'CONVERGO', 'TOGGEO', 'VERITAS',
    'CREO', 'OSTENDO', 'FOCUS'
]
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}

# --- Cohesive Flux Framework (CFF) Core ---
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
    def display(self):
        return (f"FLUXUS: {self.energy:.2f} | MEMORIA: {len(self.memory_patterns)} | "
                f"IDENTITAS: {self.identity_wave:.2f}\nGRIDUM:\n{self.grid}\n"
                f"CONTEXTUS: {self.context_embeddings}")

class Contextus:
    def __init__(self):
        self.materiae = {}
        self.focus = None
    def get_focused_materia(self):
        if not self.focus or self.focus.upper() not in self.materiae:
            raise ValueError("NULLA MATERIA IN FOCO EST")
        return self.materiae[self.focus.upper()]

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
def destruct(core):
    core.perturb(random.randint(0, 9), random.randint(0, 9), random.uniform(-1, 1))
def create(core):
    core.converge()

# --- Parser and Executor ---
def parse_latin_command(cmd):
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
    try:
        verb, inflection, num_args, literal = parse_latin_command(cmd)
    except ValueError as e: return f"ERROR: {e}"
    if verb not in KNOWN_VERBS: return f"VERBUM IGNORATUM '{verb}'"
    mod = inflection_map.get(inflection, {'mod': 1.0})['mod']
    if verb == 'CREO':
        if not literal: return "NOMEN REQUIRETUR"
        if literal in context.materiae: return f"'{literal}' IAM EXISTIT"
        context.materiae[literal] = FluxCore()
        return f"{verb}{inflection} MATERIAM '{literal}' CONFIRMATUM."
    if verb == 'FOCUS':
        if not literal: return "NOMEN REQUIRETUR"
        if literal not in context.materiae: return f"'{literal}' NON EXISTIT"
        context.focus = literal
        return f"FOCUS NUNC IN '{literal}'."
    if verb == 'OSTENDO':
        if not literal: return "NOMEN REQUIRETUR"
        if literal.upper() not in context.materiae: return f"'{literal}' NON EXISTIT"
        return context.materiae[literal.upper()].display()
    if verb == 'TOGGEO':
        return "ERROR: TOGGEO EST STATUM (TOGGEO is stateless and cannot be used in stateful context)"
    try:
        core = context.get_focused_materia()
    except ValueError as e: return f"ERROR: {e}"
    if verb == 'CONVERGO':
        create(core)
        return f"{verb}{inflection} FLUXUM COHERENTEM {core.energy:.2f}"
    if verb == 'PERTURBO':
        destruct(core)
        chunks = dynamic_chunk(num_args)
        for chunk in chunks:
            synth = triad(chunk, mod)
            core.perturb(random.randint(0,9), random.randint(0,9), synth, mod)
            core.embed_context(f'chunk_{len(core.memory_patterns)}', chunk)
        create(core)
        return f"{verb}{inflection} FLUXUM COHERENTEM {core.energy:.2f}"
    return f"{verb}{inflection} NON IMPLEMENTATUM"

# --- Test Suite for Cohesive Flux Framework ---
class TestAetherCFF(unittest.TestCase):
    def setUp(self):
        self.context = Contextus()
        print(f"\n--- Testing {self._testMethodName} ---")

    def test_cff_creation_and_focus(self):
        run_aether_command("CREO MATERIAM 'prima'", self.context)
        self.assertIn('PRIMA', self.context.materiae)
        self.assertIsInstance(self.context.materiae['PRIMA'], FluxCore)
        print("✓ CREO creates a FluxCore instance.")
        run_aether_command("FOCUS MATERIAE 'prima'", self.context)
        self.assertEqual(self.context.focus, 'PRIMA')
        print("✓ FOCUS sets context on FluxCore.")

    def test_cff_flux_and_memory(self):
        run_aether_command("CREO MATERIAM 'test'", self.context)
        run_aether_command("FOCUS MATERIAE 'test'", self.context)
        core = self.context.get_focused_materia()
        self.assertEqual(len(core.memory_patterns), 0)
        run_aether_command("PERTURBOO 1 2 3", self.context)
        self.assertEqual(len(core.memory_patterns), 2)
        print("✓ PERTURBO correctly updates memory patterns.")

    def test_cff_identity_and_context(self):
        run_aether_command("CREO MATERIAM 'test'", self.context)
        run_aether_command("FOCUS MATERIAE 'test'", self.context)
        core = self.context.get_focused_materia()
        run_aether_command("PERTURBOO 10 20 30", self.context)
        self.assertNotEqual(core.energy, 0.0)
        initial_identity = core.identity_wave
        run_aether_command("CONVERGOO", self.context)
        final_identity = core.identity_wave
        self.assertNotEqual(initial_identity, final_identity)
        print("✓ CONVERGO correctly synthesizes new identity from existing flux.")
        # MODIFICATION: Correctly assert the chunk key based on execution order.
        self.assertIn('chunk_2', core.context_embeddings)
        print("✓ PERTURBO correctly embeds context.")

# --- REPL Entry Point ---
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'repl':
        context = Contextus()
        print("--- AetherLang v0.8 (CFF Verified) ---")
        print("Verba Nota: CREO, FOCUS, OSTENDO, PERTURBO, CONVERGO")
        while True:
            cmd_input = input("aether> ")
            if cmd_input.lower() in ['exit', 'vale']: break
            if not cmd_input.strip(): continue
            print(f"< {run_aether_command(cmd_input, context)}")
        print("\n< VALE.")
    else:
        unittest.main(verbosity=2)
