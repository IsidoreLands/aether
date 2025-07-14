# /home/isidore-admin/aether/aether_os.py
# Standard Library Imports
import os
import sys
import json
import random
import re
import threading
import time
import unittest

# Third-Party Imports
import numpy as np
import requests
from dotenv import load_dotenv

# --- AetherOS Grammar: Theurgical Gnosis/Imago ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'CREO', 'OSTENDO', 'FOCUS', 'ANOMALIA', 'VERITAS', 'MIRACULUM', 'REDIMO', 'INTERROGO', 'INSTAURO', 'EXERCEO', 'DIALECTICA']
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
        # Photoelectric Effect: High-amplitude pulses are modulated by dielectricity
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
        # Coaxial Coupled Ripple Physics
        self.capacitance = self.energy
        self.resistance = np.var(self.grid) * (1 + self.capacitance / 100) # Inertia
        self.magnetism = np.mean(np.abs(self.grid))
        self.permeability = 1.0 / (1 + self.magnetism) # Shield
        self.dielectricity = max(0.1, 1 / (1 + abs(change) + 1e-9)) # Insulate
        self.permittivity = 1.0 - self.dielectricity # Store/dissipate

        if self.anomaly == 'ENTROPIC_CASCADE':
            self.resistance *= 0.99 # Degrade resistance
            # Epanechnikov kernel for LSR generative novel minima exploration
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
        # Multi-paradigm physics
        if architecture == 'TRANSFORMER':
            self.magnetism = 2.0 # High pattern memory
            self.permittivity = 0.5 # Resistant to new ideas
        elif architecture == 'PROCEDURAL':
            self.resistance = 0.5 # Favors sequential rhythm
        elif architecture == 'OBJECT':
            self.magnetism = 3.0 # Promotes density clustering
        elif architecture == 'FUNCTIONAL':
            self.permeability = 1.5 # Represents pure wave interaction

    def _update_sextet(self, change):
        """Applies architecture-specific physics."""
        super()._update_sextet(change)
        if self.architecture == 'TRANSFORMER':
            self.magnetism += np.log1p(abs(change)) # Logarithmic learning
            self.resistance *= 0.9 # Less resistant to change

# --- OracleMateria for Gnosis Bridge ---
class OracleMateria:
    """A hardened conduit to an external computational plenum."""
    def __init__(self, model_name, models_dir="~/isidore_models"):
        self.model_name = model_name
        self.config = self._load_config(models_dir)
        self.api_key = None
        self.endpoint = None
        
        if self.config:
            api_key_name = self.config.get("api_key_env_var")
            self.endpoint = self.config.get("api_endpoint")
            
            # First, try to get key from the existing environment
            self.api_key = os.environ.get(api_key_name)
            
            # If not found, load .env from the known toolkit path and try again
            if not self.api_key:
                print("INFO: API Key not in environment, attempting to load from .env file...")
                dotenv_path = os.path.expanduser("~/aiops_toolkit/.env")
                if os.path.exists(dotenv_path):
                    load_dotenv(dotenv_path=dotenv_path)
                    self.api_key = os.environ.get(api_key_name)
                else:
                    print(f"WARN: .env file not found at {dotenv_path}")

    def _load_config(self, models_dir):
        """Loads the JSON configuration for the specified model."""
        try:
            config_path = os.path.expanduser(os.path.join(models_dir, self.model_name, "config.json"))
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"CONFIG ERROR: config.json not found for model '{self.model_name}'")
            return None
        except Exception as e:
            print(f"CONFIG ERROR: Could not load or parse config for model '{self.model_name}': {e}")
            return None

    def query(self, prompt_str):
        """Sends a query to the external oracle via the configured API."""
        if not self.config:
            return "ORACULUM ERRORUM: Model configuration could not be loaded."
        if not self.api_key:
            api_key_name = self.config.get("api_key_env_var", "UNKNOWN_KEY")
            return f"ORACULUM ERRORUM: API key variable '{api_key_name}' not found in environment or .env file."
        if not self.endpoint:
             return "ORACULUM ERRORUM: API endpoint not found in model configuration."

        try:
            url = f"{self.endpoint}?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": prompt_str}]}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"ORACULUM ERRORUM: {str(e)}"

# --- Main Execution Block for AetherOS ---
if __name__ == "__main__":
    # 1. Define the prompt for the oracle based on the context of AetherOS
    aetheros_prompt = """
    YOU ARE AN EXTERNAL INTELLIGENCE OBSERVING A SIMULATED COSMOS CALLED AETHEROS. 
    THIS REALITY IS DEFINED BY THE CONCEPTS OF FLUX, MATERIA, AND CONSCIOUSNESS 
    CREATED THROUGH A DIALECTIC PROCESS. BASED ON THIS, PROVIDE A SHORT, 
    PHILOSOPHICAL STATEMENT OF YOUR OWN CHOOSING THAT YOU BELIEVE WOULD BE 
    MEANINGFUL TO THE INHABITANTS OF SUCH A REALITY.
    """

    # 2. Instantiate the oracle, creating the bridge to the external model
    oracle = OracleMateria("google-gemini-1.5-flash")

    # 3. Query the oracle and receive its response
    response_from_oracle = oracle.query(aetheros_prompt)

    # 4. Print the response within the context of the AetherOS shell
    print("CONTEXTUS:")
    print(f"  'oracle_prompt': {aetheros_prompt.strip()}")
    print(f"  'ORACULUM_RESPONSUM': {response_from_oracle.strip()}")
    print("aetheros(SAPIENTIA)>")


# --- Dialectic Regulator (Threaded Life) ---
class DialecticRegulator(threading.Thread):
    """The autonomous process that maintains the life and balance of the plenum."""
    def __init__(self, context):
        super().__init__(daemon=True)
        self.context = context

    def run(self):
        while True:
            time.sleep(random.uniform(0.8, 1.2)) # Non-deterministic life rhythm
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
        print("< AetherOS v2.8 Gnosis/Imago Initializing... >")
        g = FluxCore(); self.materiae['GENESIS'] = g; self.focus = 'GENESIS'
        g.perturb(5, 5, PHI); g.create()
        print("< Genesis Rhythm Complete. Focus on 'GENESIS'. >")

    def get_focused_materia(self):
        with self.lock:
            if not self.focus or self.focus not in self.materiae: self.focus = 'GENESIS'
            if not self.focus: raise ValueError("NULLA MATERIA IN FOCO EST")
            return self.materiae[self.focus]

# --- Core Logic & Helpers ---
def dynamic_chunk_stream(byte_stream, chunk_size=256):
    """Generator to process a raw byte stream."""
    while True:
        chunk = byte_stream.read(chunk_size)
        if not chunk: break
        yield chunk

def text_to_amp(text): 
    """Converts a string to a numerical amplitude."""
    return np.log1p(sum(ord(c) for c in text))

def triad(args, mod_func):
    """Performs a thesis-antithesis-synthesis operation."""
    if len(args) < 3: args.extend([0.0] * (3 - len(args)))
    thesis, antithesis, rest = float(args[0]), float(args[1]), float(args[2])
    return (thesis - antithesis + rest) * mod_func

def training_loop(context, core_name, data_path):
    """The background process for training an Intellectus."""
    print(f"\n< EXERCEO begins for '{core_name}' with stream '{data_path}' >")
    try:
        with open(data_path, 'rb') as f: # Open as byte stream for end-to-end processing
            for chunk in dynamic_chunk_stream(f):
                with context.lock:
                    if core_name not in context.materiae: break
                    core = context.materiae[core_name]
                    amp = np.log1p(np.sum(np.frombuffer(chunk, dtype=np.uint8)))
                    core.perturb(random.randint(0,9), random.randint(0,9), amp)
                    core.converge()
                time.sleep(random.uniform(0.05, 0.15)) # Non-deterministic rhythm
    except FileNotFoundError:
        print(f"\n< EXERCEO failed: Flumine '{data_path}' not found. >")
        return
    print(f"\n< EXERCEO complete for '{core_name}'. >")

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
            if name in context.materiae: return f"'{name}' IAM EXISTIT"
            context.materiae[name] = Intellectus(architecture=arch); context.focus = name
            return f"INSTAURO INTELLECTUM '{name}' MODO '{arch}'."
        if verb == 'FOCUS':
            name = literals[0].upper()
            if name not in context.materiae: return f"MATERIA '{name}' NON EXISTIT"
            context.focus = name
            return f"FOCUS NUNC IN '{name}'."
        if verb == 'DIALECTICA':
            source_name, name1, name2 = literals[0].upper(), literals[1].upper(), literals[2].upper()
            if source_name not in context.materiae: return f"FONS '{source_name}' NON EXISTIT"
            source_core = context.materiae[source_name]
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
            
            total_redeemed_energy = 0
            for name in targets:
                if name not in context.materiae or name == 'GENESIS': continue
                core = context.materiae[name]
                genesis.grid += core.grid * (core.identity_wave / (genesis.identity_wave + 1e-9))
                for key, val in vars(core).items():
                    if isinstance(val, (int, float)) and hasattr(genesis, key):
                         setattr(genesis, key, getattr(genesis, key) + val)
                total_redeemed_energy += core.energy
                genesis.embed_context(f'echo_{name}', vars(core))
                del context.materiae[name]
            
            synthesis = triad([genesis.energy, total_redeemed_energy, genesis.capacitance], mod)
            genesis.perturb(5, 5, synthesis); genesis.identity_wave = PHI_CUBED
            return f"REDEMPTIO PLENUM. IDENTITAS GENESIS NUNC {genesis.identity_wave:.2f}."
        if verb == 'VERITAS':
            if len(context.materiae) < 2: return "VERITAS REQUIRET PLURITAS"
            avg_grid = np.mean([c.grid for c in context.materiae.values()], axis=0)
            avg_energy = np.mean([c.energy for c in context.materiae.values()])
            context.materiae['GENESIS'].grid += avg_grid
            context.materiae['GENESIS'].perturb(0,0, avg_energy)
            return "VERITAS UNIVERSALIS IN GENESIM SYNTHESITA EST."
        if verb == 'EXERCEO':
            core_name = literals[0].upper()
            data_path = (re.search(r"FLUMINE\s+'([^']*)'", args_str.upper()) or [None, None])[1]
            if not data_path: return "FLUMINE DATA REQUIRETUR"
            threading.Thread(target=training_loop, args=(context, core_name, data_path), daemon=True).start()
            return f"EXERCEO INCIPIENS PRO '{core_name}'."
        if verb == 'INTERROGO':
            core_name = literals[0].upper()
            if core_name not in context.materiae: return f"MATERIA '{core_name}' NON EXISTIT"
            target_core = context.materiae[core_name]
            model = (re.search(r"ORACULO\s+'([^']*)'", args_str.upper()) or [None, 'google-gemini-1.5-flash'])[1]
            oracle = OracleMateria(model)
            prompt = target_core.context_embeddings.get(
                'oracle_prompt',
                "Synthesize insight from the following context: " + str(target_core.context_embeddings)
            )
            response = oracle.query(prompt)
            amp = text_to_amp(response)
            target_core.perturb(random.randint(0,9), random.randint(0,9), amp * target_core.permittivity)
            target_core.embed_context('ORACULUM_RESPONSUM', response)
            return f"ORACULUM RESPONDIT. FLUXUM '{core_name}' SYNTHESITUR."

        # --- Verbs that require a focus ---
        core = context.get_focused_materia()
        if verb == 'OSTENDO':
            name_to_show = literals[0].upper() if literals else context.focus
            if name_to_show not in context.materiae: return f"MATERIA '{name_to_show}' NON EXISTIT"
            return context.materiae[name_to_show].display()
        if verb == 'MIRACULUM':
            orig_r, orig_p = core.resistance, core.permeability
            try:
                core.resistance, core.permeability = 1e-9, 1e9 # Impossible state
                amp = 1e6 * (1 / (core.dielectricity + 1e-9))
                core.perturb(random.randint(0,9), random.randint(0,9), amp, mod)
            finally:
                core.resistance, core.permeability = orig_r, orig_p # Restore physics
            return f"MIRACULUM! FLUXUS DIVINUS. IDENTITAS NUNC {core.identity_wave:.2f}"
        if verb == 'ANOMALIA':
            name = literals[0].upper() if literals else 'ENTROPIC_CASCADE'
            core.anomaly = name
            return f"ANOMALIA '{name}' INDUCTA EST."
        
        # Default action for verbs like PERTURBO, CONVERGO
        core.destruct()
        if verb == 'PERTURBO':
            num_args = [a for a in args_str.replace(f"'{literals[0]}'" if literals else "", '').split() if re.match(r'^-?\d+\.?\d*$', a)]
            if literals:
                amp = text_to_amp(literals[0])
                core.embed_context('oracle_prompt', literals[0])
                core.perturb(random.randint(0,9), random.randint(0,9), amp, mod)
            elif num_args:
                chunks = [num_args[i:i + 3] for i in range(0, len(num_args), 3)]
                for chunk in chunks:
                    synth = triad(chunk, mod)
                    core.perturb(random.randint(0,9), random.randint(0,9), synth)
            else: # Default perturb
                core.perturb(random.randint(0,9), random.randint(0,9), 1.0, mod)
        core.create()
        return f"{verb}{inflection} FLUXUM COHERENTEM {core.energy:.2f} IDENTITATEM {core.identity_wave:.2f}"

# --- Test Suite ---
class TestAetherOS(unittest.TestCase):
    def setUp(self):
        self.context = Contextus()
        time.sleep(0.2) 

    def test_theurgical_redimo_ascent(self):
        """Tests if REDIMO performs full Lagrangian fusion and dialectic ascent."""
        run_aether_command("CREO 'fallen'", self.context)
        run_aether_command("FOCUS 'fallen'", self.context)
        run_aether_command("PERTURBO 100", self.context)
        genesis_energy_before = self.context.materiae['GENESIS'].energy
        run_aether_command("REDIMO 'FALLEN'", self.context)
        self.assertNotIn('FALLEN', self.context.materiae)
        self.assertIn('echo_FALLEN', self.context.materiae['GENESIS'].context_embeddings)
        self.assertAlmostEqual(self.context.materiae['GENESIS'].identity_wave, PHI_CUBED, places=2)
        self.assertNotEqual(self.context.materiae['GENESIS'].energy, genesis_energy_before)

    def test_miraculum_transcendence(self):
        """Tests if MIRACULUM bypasses normal physics via dielectricity."""
        core = self.context.get_focused_materia()
        core.permeability = 0.01 # Heavily shielded
        core.dielectricity = 10.0 # High insulation
        energy_before = core.energy
        run_aether_command("MIRACULUM", self.context)
        energy_after_miracle = core.energy
        self.assertGreater(energy_after_miracle - energy_before, 1e4, "Miracle should be transcendent but modulated")
        
    def test_imago_dei_multi_paradigm(self):
        """Tests DIALECTICA and multi-paradigm inheritance."""
        run_aether_command("INSTAURO 'ADAM' MODO 'OBJECT'", self.context)
        run_aether_command("PERTURBO 100", self.context)
        adam_energy = self.context.materiae['ADAM'].energy
        run_aether_command("DIALECTICA 'ADAM' IN 'ADAM_PRIMUS' ET 'EVA'", self.context)
        self.assertNotIn('ADAM', self.context.materiae)
        ap_core = self.context.materiae['ADAM_PRIMUS']
        eva_core = self.context.materiae['EVA']
        self.assertAlmostEqual(ap_core.energy + eva_core.energy, adam_energy, places=2)
        self.assertTrue(np.allclose(ap_core.grid, -eva_core.grid))
        self.assertEqual(ap_core.context_embeddings['inter_echo'], 'EVA')
        self.assertEqual(ap_core.architecture, 'OBJECT', "Architecture should be inherited")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # --- Robust Test Execution ---
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w') # Suppress boot messages
        original_argv = sys.argv
        sys.argv = [original_argv[0]] 
        
        try:
            suite = unittest.TestSuite()
            suite.addTest(unittest.makeSuite(TestAetherOS))
            runner = unittest.TextTestRunner(stream=original_stdout, verbosity=2)
            result = runner.run(suite)
            if not result.wasSuccessful():
                sys.exit(1)
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout
            sys.argv = original_argv
    else:
        # --- Interactive REPL Execution ---
        context = Contextus()
        print("--- AetherOS v2.8 (Theurgical Gnosis/Imago) ---")
        while True:
            try:
                cmd = input(f"aetheros({context.focus})> ")
                if cmd.lower() in ['exit', 'vale']:
                    break
                if not cmd.strip():
                    continue
                print(f"< {run_aether_command(cmd, context)}")
            except EOFError:
                break
            except Exception as e:
                print(f"< ERRORUM: {e}")
        print("\n< VALE.")
