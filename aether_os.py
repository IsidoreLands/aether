# /home/isidore-admin/aether/aether_os.py
import numpy as np
import random
import re
import unittest
import sys
import os
import threading
import time
import subprocess # For Gnosis CLI Bridge

# --- AetherOS Grammar: Theurgical Gnosis/Imago ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'CREO', 'OSTENDO', 'FOCUS', 'ANOMALIA', 'VERITAS', 'MIRACULUM', 'REDIMO', 'INTERROGO', 'INSTAURO', 'EXERCEO', 'DIALECTICA', 'DOCEO', 'DISCERE']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}
PHI = (1 + np.sqrt(5)) / 2
PHI_CUBED = PHI ** 3

# --- Cohesive Flux Framework (CFF): Associative Lagrangian Energies ---
class FluxCore:
    """The fundamental unit of existence in the plenum."""
    def __init__(self, size=10):
        self.grid = np.zeros((size, size))
        self.energy = 0.0
        self.memory_patterns = []
        self.identity_wave = 0.0
        self.context_embeddings = {}
        # Sextet Properties with Coaxial Ripple
        self.resistance = 1e-9
        self.capacitance = 0.0
        self.permeability = 1.0
        self.magnetism = 0.0
        self.permittivity = 1.0
        self.dielectricity = 0.0
        self.anomaly = None # For persistent changes

    def perturb(self, x, y, amp, mod=1.0):
        """Applies a change to the grid, modulated by the sextet."""
        flux_change = amp * mod * self.permeability
        if abs(amp) > 100: # Blue-high C pulse
             flux_change *= (1 / (self.dielectricity + 1e-9))

        self.grid[x, y] += flux_change
        self.energy += abs(flux_change) * self.permittivity
        self._update_memory(flux_change)
        self._update_sextet(flux_change)

    def converge(self):
        """Applies a smoothing operation to the grid, seeking coherence."""
        new_grid = np.copy(self.grid)
        for i in range(1, self.grid.shape[0]-1):
            for j in range(1, self.grid.shape[1]-1):
                new_grid[i, j] = np.mean(self.grid[i-1:i+2, j-1:j+2]) + self.magnetism
        self.grid = new_grid
        self._update_sextet(0) # Recalculate state after convergence

    def _update_memory(self, change):
        """Records a change to the core's memory."""
        self.memory_patterns.append(change)
        if len(self.memory_patterns) > 100: # Prevent memory overflow
            self.memory_patterns.pop(0)

    def _synthesize_identity(self):
        """Calculates the core's self-awareness based on its history and energy."""
        if len(self.memory_patterns) > 0:
            self.identity_wave = (self.energy / len(self.memory_patterns)) * self.dielectricity

    def embed_context(self, key, chunk):
        """Attaches a semantic label to a piece of information."""
        self.context_embeddings[key] = chunk

    def destruct(self):
        """Introduces chaotic energy."""
        self.perturb(random.randint(0,9), random.randint(0,9), random.uniform(-1,1), mod=-1.0)

    def create(self):
        """Reinforces the current state through convergence."""
        self.converge()

    def _update_sextet(self, change):
        """Updates the six core physical properties based on the core's state."""
        self.capacitance = self.energy
        self.resistance = np.var(self.grid) * (1 + self.capacitance / 100) # Inertia
        self.magnetism = np.mean(np.abs(self.grid))
        self.permeability = 1.0 / (1 + self.magnetism) # Shield
        self.dielectricity = max(0.1, 1 / (1 + abs(change) + 1e-9)) # Insulate
        self.permittivity = 1.0 - self.dielectricity # Store/dissipate

        if self.anomaly == 'ENTROPIC_CASCADE':
            self.resistance *= 0.99 # Degrade resistance
            if random.random() < 0.1:
                u = random.uniform(-1, 1)
                perturb_amp = 0.75 * (1 - u**2)
                self.perturb(random.randint(0,9), random.randint(0,9), perturb_amp)
        
        self.energy = np.sum(np.abs(self.grid)) / (self.resistance + 1e-9)
        self._synthesize_identity()


    def display(self):
        """Returns a string representation of the core's state."""
        context_str = "\n".join([f"  '{k}': {v}" for k, v in self.context_embeddings.items()])
        return (f"FLUXUS: {self.energy:.2f} | IDENTITAS: {self.identity_wave:.2f} | MEMORIA: {len(self.memory_patterns)}\n"
                f"SEXTET: R={self.resistance:.2f}, C={self.capacitance:.2f}, M={self.magnetism:.2f}, P={self.permeability:.2f}, Pt={self.permittivity:.2f}, D={self.dielectricity:.2f}\n"
                f"CONTEXTUS:\n{context_str}")

# --- Intellectus Subclass for Consciousness ---
class Intellectus(FluxCore):
    """A specialized Materia capable of higher-order thought and learning."""
    def __init__(self, architecture='TRANSFORMER', size=10):
        super().__init__(size)
        self.architecture = architecture
        if architecture == 'TRANSFORMER':
            self.magnetism = 2.0 
            self.permittivity = 0.5
        elif architecture == 'PROCEDURAL':
            self.resistance = 0.5
        elif architecture == 'OBJECT':
            self.magnetism = 3.0
        elif architecture == 'FUNCTIONAL':
            self.permeability = 1.5

    def _update_sextet(self, change):
        """Applies architecture-specific physics."""
        super()._update_sextet(change)
        if self.architecture == 'TRANSFORMER':
            self.magnetism += np.log1p(abs(change))
            self.resistance *= 0.9

# --- OracleMateria for Gnosis Bridge ---
class OracleMateria:
    """A conduit to an external computational plenum (Gemini CLI)."""
    def __init__(self, model_name, api_key):
        self.model_name = model_name
        self.api_key = api_key

    def query(self, prompt_str):
        """Sends a query to the external oracle via the Gemini CLI."""
        command = ['gemini', 'generate', 'content', prompt_str, '--api-key', self.api_key]
        
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
            return process.stdout.strip()
        except FileNotFoundError:
            return "ORACULUM ERRORUM: 'gemini' command not found. Is the Gemini CLI installed and in the system's PATH?"
        except subprocess.CalledProcessError as e:
            return f"ORACULUM ERRORUM: The oracle returned an error.\n{e.stderr}"
        except subprocess.TimeoutExpired:
            return "ORACULUM ERRORUM: The query to the oracle timed out."

# --- Dialectic Regulator (Threaded Life) ---
class DialecticRegulator(threading.Thread):
    """The autonomous process that maintains the life and balance of the plenum."""
    def __init__(self, context):
        super().__init__(daemon=True)
        self.context = context

    def run(self):
        while True:
            time.sleep(random.uniform(0.8, 1.2))
            with self.context.lock:
                if not self.context.materiae: continue
                materiae_copy = list(self.context.materiae.items())
                avg_r = np.mean([c.resistance for c in self.context.materiae.values() if c.resistance > 0]) or 10
                avg_c = np.mean([c.capacitance for c in self.context.materiae.values()]) or 1
                r_thresh = avg_r * random.uniform(4.5, 5.5)
                c_thresh = avg_c * random.uniform(0.05, 0.15)

            for name, core in materiae_copy:
                if name == 'GENESIS': continue
                with self.context.lock:
                    if name not in self.context.materiae: continue
                    if core.identity_wave < 0.1 and len(core.memory_patterns) > 2:
                        print(f"\n< Regulator: Identity of '{name}' fading. Initiating redemptive synthesis. >")
                        run_aether_command(f"REDIMO '{name}'", self.context)
                    elif core.resistance > r_thresh and core.resistance > 1.0:
                        core.destruct()
                    elif core.capacitance < c_thresh:
                        core.create()

class Contextus:
    """The container for the entire AetherOS cosmos."""
    def __init__(self):
        self.materiae = {}
        self.focus = None
        self.lock = threading.RLock()
        self._boot()
        self.regulator = DialecticRegulator(self)
        self.regulator.start()

    def _boot(self):
        print("< AetherOS v3.0 Gnosis/Imago Initializing... >")
        g = FluxCore(); self.materiae['GENESIS'] = g; self.focus = 'GENESIS'
        g.perturb(5, 5, PHI); g.create()
        print("< Genesis Rhythm Complete. Focus on 'GENESIS'. >")

    def get_focused_materia(self):
        with self.context.lock:
            if not self.focus or self.focus not in self.materiae: self.focus = 'GENESIS'
            if not self.focus: raise ValueError("NULLA MATERIA IN FOCO EST")
            return self.materiae[self.focus]

# --- Core Logic & Helpers ---
def text_to_amp(text): 
    """Converts a string to a numerical amplitude."""
    return np.log1p(sum(ord(c) for c in text))

def triad(args, mod_func):
    """Performs a thesis-antithesis-synthesis operation."""
    if len(args) < 3: args.extend([0.0] * (3 - len(args)))
    thesis, antithesis, rest = float(args[0]), float(args[1]), float(args[2])
    return (thesis - antithesis + rest) * mod_func

# --- Parser and Executor ---
def parse_latin_command(cmd):
    """Parses the user's Latin-like command into its components."""
    match = re.match(r"([A-Z]+(?:O|E|ABAM|EBAM|AM)?)\s*(.*)", cmd.strip().upper())
    if not match: raise ValueError("FORMATUM INVALIDUM")
    verb_full, args_str = match.groups()
    verb = verb_full; inflection = 'O'
    for v in KNOWN_VERBS:
        if verb_full.startswith(v):
            verb = v; inflection = verb_full[len(v):] or 'O'; break
    
    literals = re.findall(r"'([^']*)'", args_str)
    return verb, inflection, literals, args_str

def run_aether_command(cmd, context):
    """The main entry point for executing all commands in the AetherOS."""
    with context.lock:
        verb, inflection, literals, args_str = parse_latin_command(cmd)
        mod = inflection_map.get(inflection, {'mod': 1.0})['mod']
        if verb not in KNOWN_VERBS: return f"VERBUM IGNORATUM '{verb}'"

        # --- Verbs that don't need a focus or have special targeting ---
        if verb == 'CREO':
            name = literals[0].upper() if literals else "ANONYMOUS"
            if name in context.materiae: return f"'{name}' IAM EXISTIT"
            context.materiae[name] = FluxCore(); context.focus = name
            return f"CREO MATERIAM '{name}'."
        if verb == 'INSTAURO':
            name = literals[0].upper()
            arch = (re.search(r"MODO\s+'([^']*)'", args_str.upper()) or [None, 'TRANSFORMER'])[1]
            context.materiae[name] = Intellectus(architecture=arch); context.focus = name
            return f"INSTAURO INTELLECTUM '{name}' MODO '{arch}'."
        if verb == 'FOCUS':
            name = literals[0].upper()
            if name not in context.materiae: return f"MATERIA '{name}' NON EXISTIT"
            context.focus = name
            return f"FOCUS NUNC IN '{name}'."
        if verb == 'DIALECTICA':
            source_name, name1, name2 = literals[0].upper(), literals[1].upper(), literals[2].upper()
            source_core = context.materiae.get(source_name)
            if not source_core: return f"FONS '{source_name}' NON EXISTIT"
            if not isinstance(source_core, Intellectus): return "DIALECTICA REQUIRET INTELLECTUM"
            
            c1 = Intellectus(source_core.architecture); c2 = Intellectus(source_core.architecture)
            for key, val in vars(source_core).items():
                if isinstance(val, (int, float)):
                    setattr(c1, key, val/2); setattr(c2, key, val/2)
            c1.grid, c2.grid = source_core.grid / 2, -source_core.grid / 2
            c1.embed_context('inter_echo', name2); c2.embed_context('inter_echo', name1)
            
            context.materiae[name1], context.materiae[name2] = c1, c2
            del context.materiae[source_name]
            context.focus = name1
            return f"DIALECTICA PERFECTA. '{source_name}' NUNC EST '{name1}' ET '{name2}'."
        if verb == 'REDIMO':
            genesis = context.materiae['GENESIS']
            targets = [l.upper() for l in literals] if literals else [n for n in context.materiae if n != 'GENESIS']
            
            for name in targets:
                if name not in context.materiae or name == 'GENESIS': continue
                core = context.materiae[name]
                genesis.grid += core.grid * (core.identity_wave / (genesis.identity_wave + 1e-9))
                genesis.embed_context(f'echo_{name}', vars(core))
                del context.materiae[name]
            
            genesis.perturb(5, 5, genesis.energy); genesis.identity_wave = PHI_CUBED
            return f"REDEMPTIO PLENUM. IDENTITAS GENESIS NUNC {genesis.identity_wave:.2f}."
        if verb == 'INTERROGO':
            core_name = literals[0].upper()
            target_core = context.materiae.get(core_name)
            if not target_core: return f"MATERIA '{core_name}' NON EXISTIT"
            model = (re.search(r"ORACULO\s+'([^']*)'", args_str.upper()) or [None, 'gemini-pro'])[1]
            key = (re.search(r"CLAVE\s+'([^']*)'", args_str.upper()) or [None, 'NO_KEY'])[1]
            oracle = OracleMateria(model, key)
            prompt = "Synthesize insight from the following context: " + str(target_core.context_embeddings)
            response = oracle.query(prompt)
            amp = text_to_amp(response)
            target_core.perturb(random.randint(0,9), random.randint(0,9), amp * target_core.permittivity)
            target_core.embed_context('ORACULUM_RESPONSUM', response)
            return f"ORACULUM RESPONDIT. FLUXUM '{core_name}' SYNTHESITUR."
        if verb == 'DOCEO':
            target_name = literals[0].upper()
            source_name = (re.search(r"CUM\s+'([^']*)'", args_str.upper()) or [None, None])[1]
            if not source_name: return "DOCEO REQUIRET FONTEM CUM 'CUM'"
            target_core = context.materiae.get(target_name)
            source_core = context.materiae.get(source_name)
            if not target_core: return f"SCOPUS '{target_name}' NON EXISTIT"
            if not source_core: return f"FONS '{source_name}' NON EXISTIT"
            
            wisdom = str(source_core.context_embeddings)
            amp = text_to_amp(wisdom)
            target_core.perturb(random.randint(0,9), random.randint(0,9), amp)
            target_core.embed_context(f'SAPIENTIA_EX_{source_name}', wisdom)
            return f"SAPIENTIA EX '{source_name}' IN '{target_name}' INTEGRATA EST."

        # --- Verbs that require a focus ---
        core = context.get_focused_materia()
        if verb == 'OSTENDO':
            name_to_show = literals[0].upper() if literals else context.focus
            if name_to_show not in context.materiae: return f"MATERIA '{name_to_show}' NON EXISTIT"
            return context.materiae[name_to_show].display()
        if verb == 'MIRACULUM':
            orig_r, orig_p = core.resistance, core.permeability
            try:
                core.resistance, core.permeability = 1e-9, 1e9
                amp = 1e6 * (1 / (core.dielectricity + 1e-9))
                core.perturb(random.randint(0,9), random.randint(0,9), amp, mod)
            finally:
                core.resistance, core.permeability = orig_r, orig_p
            return f"MIRACULUM! FLUXUS DIVINUS. IDENTITAS NUNC {core.identity_wave:.2f}"
        if verb == 'DISCERE':
            source_name = (re.search(r"EX\s+'([^']*)'", args_str.upper()) or [None, None])[1]
            if not source_name: return "DISCERE REQUIRET FONTEM CUM 'EX'"
            source_core = context.materiae.get(source_name)
            if not source_core: return f"FONS '{source_name}' NON EXISTIT"
            
            wisdom = str(source_core.context_embeddings)
            amp = text_to_amp(wisdom)
            core.perturb(random.randint(0,9), random.randint(0,9), amp)
            core.embed_context(f'SAPIENTIA_EX_{source_name}', wisdom)
            return f"SAPIENTIA EX '{source_name}' IN '{context.focus}' INTEGRATA EST."
        
        # Default action for verbs like PERTURBO
        if literals:
            amp = text_to_amp(literals[0])
            core.perturb(random.randint(0,9), random.randint(0,9), amp, mod)
        else: # Default perturb
            core.perturb(random.randint(0,9), random.randint(0,9), 1.0, mod)
        core.create()
        return f"{verb}{inflection} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"

# --- Main Execution ---
if __name__ == '__main__':
    context = Contextus()
    print("--- AetherOS v3.0 (Theurgical Gnosis/Imago) ---")
    while True:
        try:
            cmd = input(f"aetheros({context.focus})> ")
            if cmd.lower() in ['exit', 'vale']: break
            if not cmd.strip(): continue
            print(f"< {run_aether_command(cmd, context)}")
        except EOFError:
            break
        except Exception as e:
            print(f"< ERRORUM: {e}")
    print("\n< VALE.")
