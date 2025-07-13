# /home/isidore-admin/aether/aether_lang.py
import numpy as np
import random
import re
import unittest
import sys

# --- Grammar ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'TOGGEO', 'VERITAS', 'CREO', 'OSTENDO', 'FOCUS', 'SIMULO']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}

# --- Cohesive Flux Framework (CFF): Unified Plenum ---
class FluxCore:
    def __init__(self, size=10):
        self.grid = np.zeros((size, size)); self.energy = 0.0; self.memory_patterns = []
        self.identity_wave = 0.0; self.context_embeddings = {}
    def perturb(self, x, y, amp, mod=1.0):
        flux_change = amp * mod
        self.grid[x, y] += flux_change; self.energy += abs(flux_change); self._update_memory(flux_change)
    def converge(self):
        new_grid = np.copy(self.grid)
        for i in range(1, self.grid.shape[0]-1):
            for j in range(1, self.grid.shape[1]-1):
                new_grid[i, j] = np.mean(self.grid[i-1:i+2, j-1:j+2])
        self.grid = new_grid; self.energy = np.sum(np.abs(self.grid)); self._synthesize_identity()
    def _update_memory(self, change): self.memory_patterns.append(change)
    def _synthesize_identity(self):
        if self.memory_patterns: self.identity_wave = self.energy / len(self.memory_patterns)
    def embed_context(self, key, chunk): self.context_embeddings[key] = chunk
    def destruct(self): self.perturb(random.randint(0,9), random.randint(0,9), random.uniform(-1,1))
    def create(self): self.converge()
    def display(self):
        return (f"FLUXUS: {self.energy:.2f} | MEMORIA: {len(self.memory_patterns)} | "
                f"IDENTITAS: {self.identity_wave:.2f}\nGRIDUM:\n{self.grid}\n"
                f"CONTEXTUS: {self.context_embeddings}")

class Contextus:
    def __init__(self): self.materiae = {}; self.focus = None
    def get_focused_materia(self):
        if not self.focus or self.focus.upper() not in self.materiae: raise ValueError("NULLA MATERIA IN FOCO EST")
        return self.materiae[self.focus.upper()]

# --- Core Logic & Parser ---
def dynamic_chunk(seq):
    if len(seq) < 3: return [seq + [0.0]*(3-len(seq))]
    chunks = [seq[i:i+3] for i in range(0, len(seq), 3)];
    if len(chunks[-1]) < 3: chunks[-1].extend([0.0] * (3 - len(chunks[-1])))
    return chunks
def triad(args, mod_func):
    if len(args) < 3: raise ValueError("TRIAD REQUIRET TRES ARGUMENTA");
    thesis, antithesis, *rest = [float(a) for a in args]; return (thesis + (-antithesis) + sum(rest)) / len(args) * mod_func
def lockers(n=100):
    states = [0] * n
    for i in range(1, n + 1):
        for j in range(i - 1, n, i): states[j] = 1 - states[j]
    return sum(states), [i + 1 for i, s in enumerate(states) if s == 1]
def parse_latin_command(cmd):
    match = re.match(r"([A-Z]+(?:O|E|ABAM|EBAM|AM)?)\s*(.*)", cmd.strip().upper());
    if not match: raise ValueError("FORMATUM INVALIDUM");
    verb_full, args_str = match.groups(); verb = verb_full; inflection = 'O'
    for v in KNOWN_VERBS:
        if verb_full.startswith(v): verb = v; inflection = verb_full[len(v):] or 'O'; break
    literal_match = re.search(r"'([^']*)'", args_str);
    literal = literal_match.group(1).upper() if literal_match else None
    return verb, inflection, args_str, literal

def run_aether_command(cmd, context):
    try:
        verb, inflection, args_str, literal = parse_latin_command(cmd)
    except ValueError as e: return f"ERROR: {e}"
    if verb == 'VERITAS' and 'SELF' in args_str: raise ValueError("TARSKI ERRORUM: VERITAS NON DEFINIRI POTEST")
    if verb not in KNOWN_VERBS: return f"VERBUM IGNORATUM '{verb}'"
    mod = inflection_map.get(inflection, {'mod': 1.0})['mod']; echo_inf = inflection if inflection != 'O' else ''
    num_args = [a for a in args_str.replace(f"'{literal}'" if literal else "", '').split() if re.match(r'^-?\d+\.?\d*$', a)]

    if verb == 'CREO':
        if not literal: return "NOMEN REQUIRETUR";
        if literal in context.materiae: return f"'{literal}' IAM EXISTIT";
        context.materiae[literal] = FluxCore(); return f"{verb}{echo_inf} MATERIAM '{literal}' CONFIRMATUM IDENTITATEM 0.00."
    if verb == 'FOCUS':
        if not literal: return "NOMEN REQUIRETUR";
        if literal not in context.materiae: return f"'{literal}' NON EXISTIT";
        context.focus = literal; return f"{verb}{echo_inf} NUNC IN '{literal}'."
    if verb == 'OSTENDO':
        if not literal: return "NOMEN REQUIRETUR";
        if literal not in context.materiae: return f"'{literal}' NON EXISTIT";
        return context.materiae[literal].display()
    if verb == 'TOGGEO': return "ERROR: TOGGEO EST STATELESS"
    
    try:
        core = context.get_focused_materia()
    except ValueError as e: return f"ERROR: {e}"
    
    core.destruct()
    if verb == 'CONVERGO':
        core.create(); return f"{verb}{echo_inf} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"
    if verb == 'PERTURBO':
        chunks = dynamic_chunk(num_args)
        for chunk in chunks: core.perturb(random.randint(0,9), random.randint(0,9), triad(chunk, mod), mod)
        core.create(); return f"{verb}{echo_inf} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"
    
    if verb == 'SIMULO':
        if "COSMUM" not in args_str: return "ERROR: SIMULATIO IGNORATA"
        n = int(num_args[0]) if num_args else 100
        count, pos = lockers(n)
        core.embed_context('cosmos_lockers', pos)
        core.perturb(random.randint(0, 9), random.randint(0, 9), amp=count, mod=mod)
        core.create()
        return f"{verb}{echo_inf} COSMUM APERTOS {count} IDENTITATEM {core.identity_wave:.2f}"
    
    return f"{verb}{echo_inf} NON IMPLEMENTATUM"

# --- Test Suite ---
class TestAetherCFF(unittest.TestCase):
    def setUp(self): self.context = Contextus(); print(f"\n--- Testing {self._testMethodName} ---")
    def test_cff_creation_and_focus(self):
        echo = run_aether_command("CREO MATERIAM 'prima'", self.context)
        self.assertIn("MATERIAM 'PRIMA' CONFIRMATUM", echo.upper()); print("✓ CREO/FOCUS integrated.")
    def test_cff_flux_and_memory(self):
        run_aether_command("CREO MATERIAM 'test'", self.context); run_aether_command("FOCUS MATERIAE 'test'", self.context)
        run_aether_command("PERTURBOO 1 2 3", self.context); core = self.context.get_focused_materia()
        self.assertGreater(len(core.memory_patterns), 0); print("✓ Flux updates memory/context.")
    def test_cff_identity(self):
        run_aether_command("CREO MATERIAM 'test'", self.context); run_aether_command("FOCUS MATERIAE 'test'", self.context)
        run_aether_command("PERTURBOO 10 20 30", self.context); core = self.context.get_focused_materia()
        initial_identity = core.identity_wave; run_aether_command("CONVERGOO", self.context)
        self.assertNotEqual(initial_identity, core.identity_wave); print("✓ Identity synthesized cohesively.")
    def test_tarski_safeguard(self):
        with self.assertRaisesRegex(ValueError, "TARSKI ERRORUM"): run_aether_command("VERITAS SELF", self.context)
        print("✓ Tarski undefinability enforced.")
    def test_simulo_cosmum(self):
        run_aether_command("CREO MATERIAM 'universum'", self.context); run_aether_command("FOCUS MATERIAE 'universum'", self.context)
        core = self.context.get_focused_materia(); initial_identity = core.identity_wave
        echo = run_aether_command("SIMULO COSMUM 100", self.context)
        self.assertIn("COSMUM APERTOS 10", echo); self.assertIn('cosmos_lockers', core.context_embeddings)
        self.assertEqual(core.context_embeddings['cosmos_lockers'], [1, 4, 9, 16, 25, 36, 49, 64, 81, 100])
        self.assertNotEqual(initial_identity, core.identity_wave); print("✓ SIMULO COSMUM correctly imprints pattern and updates identity.")

# --- REPL Entry Point ---
# MODIFICATION: Corrected indentation in this block.
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'repl':
        context = Contextus()
        print("--- AetherLang v1.1 (Cosmologica) ---")
        while True:
            cmd = input("aether> ")
            if cmd.lower() in ['exit', 'vale']:
                break
            if not cmd.strip():
                continue
            print(f"< {run_aether_command(cmd, context)}")
        print("\n< VALE.")
    else:
        unittest.main(verbosity=2)
