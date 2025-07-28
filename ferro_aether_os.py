# aether_os.py
#
# Description:
# This is the main entry point and runtime for the AetherOS. It orchestrates
# the simulation, manages the state of all 'Materia', and provides the
# user-facing REPL (Read-Eval-Print Loop) for interacting with the system.

import os
import re
import sys
import threading
import time
import random
import numpy as np
import unittest

# Import components from the other modules
from flux_core import FluxCore, Intellectus
from oracle import OracleMateria

# --- AetherOS Grammar and Constants ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'CREO', 'OSTENDO', 'FOCUS', 'ANOMALIA', 'VERITAS', 
               'MIRACULUM', 'REDIMO', 'INTERROGO', 'INSTAURO', 'EXERCEO', 'DIALECTICA', 
               'DOCEO', 'DISCERE']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}
PHI = (1 + np.sqrt(5)) / 2


# --- Helper Functions ---
def text_to_amp(text):
    """Converts a string to a numerical amplitude using a log scale."""
    return np.log1p(sum(ord(c) for c in text))

def dynamic_chunk_stream(byte_stream, chunk_size=256):
    """Generator to process a raw byte stream into chunks."""
    while True:
        chunk = byte_stream.read(chunk_size)
        if not chunk: break
        yield chunk

def training_loop(context, core_name, data_path):
    """The background process for training an Intellectus from a data file."""
    print(f"\n< EXERCEO begins for '{core_name}' with stream '{data_path}' >")
    try:
        with open(data_path, 'rb') as f:
            for chunk in dynamic_chunk_stream(f):
                with context.lock:
                    if core_name not in context.materiae:
                        print(f"\n< EXERCEO aborted: '{core_name}' no longer exists. >")
                        break
                    core = context.materiae[core_name]
                    amp = np.log1p(np.sum(np.frombuffer(chunk, dtype=np.uint8)))
                    core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), amp)
                    core.converge()
                time.sleep(random.uniform(0.05, 0.15))
    except FileNotFoundError:
        print(f"\n< EXERCEO failed: Flumine '{data_path}' not found. >")
        return
    print(f"\n< EXERCEO complete for '{core_name}'. >")


# --- Autonomous System Regulator ---
class DialecticRegulator(threading.Thread):
    """The 'heartbeat' of the OS, maintaining balance and driving emergent behavior."""
    def __init__(self, context):
        super().__init__(daemon=True)
        self.context = context

    def run(self):
        while True:
            time.sleep(random.uniform(0.8, 1.2))  # Non-deterministic life rhythm
            with self.context.lock:
                if not self.context.materiae: continue
                
                materiae_copy = list(self.context.materiae.values())
                if len(materiae_copy) <= 1: continue

                avg_r = np.mean([c.resistance for c in materiae_copy if c.resistance > 0]) or 1e-9
                avg_c = np.mean([c.capacitance for c in materiae_copy]) or 1.0
                
                r_thresh = avg_r * random.uniform(4.5, 5.5) # Threshold for instability
                c_thresh = avg_c * random.uniform(0.05, 0.15) # Threshold for stagnation

                for name, core in list(self.context.materiae.items()):
                    if name == 'GENESIS': continue
                    
                    if core.identity_wave < 0.1 and len(core.memory_patterns) > 2:
                        print(f"\n< Regulator: Identity of '{name}' fading. Initiating redemptive synthesis. >")
                        self.context.execute_command(f"REDIMO '{name}'")
                    elif core.resistance > r_thresh and core.resistance > 1.0:
                        core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), -1.0)
                    elif core.capacitance < c_thresh:
                        core.converge()


# --- Main Application Context and Executor ---
class Contextus:
    """The container for the entire AetherOS cosmos and command execution."""
    def __init__(self):
        self.materiae = {}
        self.focus = None
        self.lock = threading.RLock()
        self.verb_handlers = self._get_verb_handlers()
        
        self._boot()
        self.regulator = DialecticRegulator(self)
        self.regulator.start()

    def _boot(self):
        print("< AetherOS v3.3 Gnosis/Imago (Final Modular) Initializing... >")
        g = FluxCore()
        self.materiae['GENESIS'] = g
        self.focus = 'GENESIS'
        g.perturb(5, 5, PHI)
        g.converge()
        print("< Genesis Rhythm Complete. Focus on 'GENESIS'. >")

    def get_focused_materia(self):
        with self.lock:
            if not self.focus or self.focus not in self.materiae:
                self.focus = 'GENESIS' if 'GENESIS' in self.materiae else None
            if not self.focus:
                raise ValueError("NULLA MATERIA IN FOCO EST")
            return self.materiae[self.focus]

    def execute_command(self, cmd):
        """Parses and executes a command using the handler mapping."""
        try:
            verb, inflection, literals, args_str = self._parse_latin_command(cmd)
            mod = inflection_map.get(inflection, {'mod': 1.0})['mod']

            handler = self.verb_handlers.get(verb)
            if handler:
                return handler(inflection, mod, literals, args_str)
            else:
                return f"VERBUM IGNORATUM '{verb}'"
        except Exception as e:
            return f"ERRORUM INTERNUM: {e}"

    def _parse_latin_command(self, cmd):
        """Parses the user's command into its components."""
        match = re.match(r"([A-Z]+(?:O|E|ABAM|EBAM|AM)?)\s*(.*)", cmd.strip().upper())
        if not match: raise ValueError("FORMATUM INVALIDUM")
        
        verb_full, args_str = match.groups()
        verb, inflection = verb_full, 'O'
        
        for v in KNOWN_VERBS:
            if verb_full.startswith(v):
                verb = v
                inflection = verb_full[len(v):] or 'O'
                break
        
        literals = re.findall(r"'([^']*)'", args_str)
        return verb, inflection, literals, args_str

    # --- Verb Handler Methods ---
    def _get_verb_handlers(self):
        """Maps verb strings to their handler methods."""
        return {
            'CREO': self._handle_creo, 'INSTAURO': self._handle_instauro,
            'FOCUS': self._handle_focus, 'OSTENDO': self._handle_ostendo,
            'PERTURBO': self._handle_perturbo, 'CONVERGO': self._handle_convergo,
            'REDIMO': self._handle_redimo, 'INTERROGO': self._handle_interrogo,
            'EXERCEO': self._handle_exerceo, 'DOCEO': self._handle_doceo,
            'DISCERE': self._handle_discere, 'DIALECTICA': self._handle_dialectica,
            'VERITAS': self._handle_veritas, 'MIRACULUM': self._handle_miraculum,
            'ANOMALIA': self._handle_anomalia,
        }

    def _handle_creo(self, inf, mod, lit, args):
        name = lit[0].upper() if lit else "ANONYMOUS"
        if name in self.materiae: return f"'{name}' IAM EXISTIT"
        self.materiae[name] = FluxCore()
        self.focus = name
        return f"CREO MATERIAM '{name}'."

    def _handle_instauro(self, inf, mod, lit, args):
        name = lit[0].upper()
        arch = (re.search(r"MODO\s+'([^']*)'", args.upper()) or [None, 'TRANSFORMER'])[1]
        if name in self.materiae: return f"'{name}' IAM EXISTIT"
        self.materiae[name] = Intellectus(architecture=arch)
        self.focus = name
        return f"INSTAURO INTELLECTUM '{name}' MODO '{arch}'."
    
    def _handle_focus(self, inf, mod, lit, args):
        name = lit[0].upper()
        if name not in self.materiae: return f"MATERIA '{name}' NON EXISTIT"
        self.focus = name
        return f"FOCUS NUNC IN '{name}'."
    
    def _handle_ostendo(self, inf, mod, lit, args):
        name_to_show = lit[0].upper() if lit else self.focus
        if name_to_show not in self.materiae: return f"MATERIA '{name_to_show}' NON EXISTIT"
        return self.materiae[name_to_show].display()

    def _handle_perturbo(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        amp = text_to_amp(lit[0]) if lit else 1.0
        if lit: core.context_embeddings['last_input'] = lit[0]
        core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), amp, mod)
        return f"PERTURBO. FLUXUM {core.energy:.2f}."

    def _handle_convergo(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        core.converge()
        return f"CONVERGO. FLUXUM {core.energy:.2f}."

    def _handle_redimo(self, inf, mod, lit, args):
        genesis = self.materiae.get('GENESIS')
        if not genesis: return "REDEMPTIO IMPOSSIBILIS: GENESIS NON EXISTIT."
        
        targets = [l.upper() for l in lit] if lit else [n for n in self.materiae if n != 'GENESIS']
        if not targets: return "NULLA MATERIA AD REDIMENDUM."

        for name in targets:
            if name not in self.materiae or name == 'GENESIS': continue
            core = self.materiae.pop(name)
            
            props_to_redeem = ['energy', 'resistance', 'capacitance', 'magnetism', 'permittivity', 'dielectricity']
            for prop in props_to_redeem:
                setattr(genesis, prop, getattr(genesis, prop, 0) + getattr(core, prop, 0))
            
            genesis.grid += core.grid * (core.identity_wave / (genesis.identity_wave + 1e-9))
            genesis.context_embeddings[f'echo_of_{name}'] = core.display()
        
        genesis.converge()
        return f"REDEMPTIO PLENUM. GENESIS CONFIRMATUR."

    def _handle_interrogo(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        model = (re.search(r"ORACULO\s+'([^']*)'", args.upper()) or [None, 'google-gemini-1.5-flash'])[1]
        oracle = OracleMateria(model)
        
        prompt = lit[0] if lit else core.context_embeddings.get('last_input', "Describe your current state.")
        response = oracle.query(prompt)
        
        amp = text_to_amp(response)
        core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), amp * core.permittivity)
        core.context_embeddings['ORACULUM_RESPONSUM'] = response
        return f"ORACULUM RESPONDIT. FLUXUM '{self.focus}' SYNTHESITUR."

    def _handle_exerceo(self, inf, mod, lit, args):
        core_name = lit[0].upper()
        data_path = (re.search(r"FLUMINE\s+'([^']*)'", args.upper()) or [None, None])[1]
        if not data_path: return "EXERCEO REQUIRET FLUMINE DATA"
        if core_name not in self.materiae: return f"MATERIA '{core_name}' NON EXISTIT"
        
        threading.Thread(target=training_loop, args=(self, core_name, data_path), daemon=True).start()
        return f"EXERCEO INCIPIENS PRO '{core_name}'."

    def _handle_doceo(self, inf, mod, lit, args):
        target_name = lit[0].upper()
        source_name = (re.search(r"CUM\s+'([^']*)'", args.upper()) or [None, None])[1]
        if not source_name: return "DOCEO REQUIRET FONTEM CUM 'CUM'"
        
        target_core, source_core = self.materiae.get(target_name), self.materiae.get(source_name)
        if not target_core: return f"SCOPUS '{target_name}' NON EXISTIT"
        if not source_core: return f"FONS '{source_name}' NON EXISTIT"
        
        wisdom = str(source_core.context_embeddings)
        amp = text_to_amp(wisdom)
        target_core.perturb(random.randint(0, target_core.size-1), random.randint(0, target_core.size-1), amp)
        target_core.context_embeddings[f'SAPIENTIA_EX_{source_name}'] = wisdom
        return f"SAPIENTIA EX '{source_name}' IN '{target_name}' INTEGRATA EST."

    def _handle_discere(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        source_name = (re.search(r"EX\s+'([^']*)'", args.upper()) or [None, None])[1]
        if not source_name: return "DISCERE REQUIRET FONTEM CUM 'EX'"
        
        source_core = self.materiae.get(source_name)
        if not source_core: return f"FONS '{source_name}' NON EXISTIT"
        
        wisdom = str(source_core.context_embeddings)
        amp = text_to_amp(wisdom)
        core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), amp)
        core.context_embeddings[f'SAPIENTIA_EX_{source_name}'] = wisdom
        return f"SAPIENTIA EX '{source_name}' IN '{self.focus}' INTEGRATA EST."

    def _handle_dialectica(self, inf, mod, lit, args):
        if len(lit) < 3: return "DIALECTICA REQUIRET FONTEM ET DUO NOMINA NOVA"
        source_name, name1, name2 = lit[0].upper(), lit[1].upper(), lit[2].upper()
        
        source_core = self.materiae.get(source_name)
        if not source_core: return f"FONS '{source_name}' NON EXISTIT"
        if not isinstance(source_core, Intellectus): return "DIALECTICA REQUIRET INTELLECTUM"
        
        c1 = Intellectus(source_core.architecture); c2 = Intellectus(source_core.architecture)
        for key, val in vars(source_core).items():
            if isinstance(val, (int, float)):
                setattr(c1, key, val/2); setattr(c2, key, val/2)
        c1.grid, c2.grid = source_core.grid / 2, -source_core.grid / 2
        c1.context_embeddings['inter_echo'] = name2; c2.context_embeddings['inter_echo'] = name1
        
        self.materiae[name1], self.materiae[name2] = c1, c2
        del self.materiae[source_name]
        self.focus = name1
        return f"DIALECTICA PERFECTA. '{source_name}' NUNC EST '{name1}' ET '{name2}'."

    def _handle_veritas(self, inf, mod, lit, args):
        if len(self.materiae) < 2: return "VERITAS REQUIRET PLURITAS"
        genesis = self.materiae.get('GENESIS')
        if not genesis: return "VERITAS REQUIRET GENESIM"

        all_grids = [c.grid for c in self.materiae.values() if c is not genesis]
        avg_grid = np.mean(all_grids, axis=0) if all_grids else np.zeros_like(genesis.grid)
        avg_energy = np.mean([c.energy for c in self.materiae.values() if c is not genesis]) or 0
        
        genesis.grid += avg_grid
        genesis.perturb(0, 0, avg_energy)
        return "VERITAS UNIVERSALIS IN GENESIM SYNTHESITA EST."

    def _handle_miraculum(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        orig_r, orig_p = core.resistance, core.permeability
        try:
            core.resistance, core.permeability = 1e-9, 1e9 # Impossible state
            amp = 1e6 * (1 / (core.dielectricity + 1e-9))
            core.perturb(random.randint(0, core.size-1), random.randint(0, core.size-1), amp, mod)
        finally:
            core.resistance, core.permeability = orig_r, orig_p # Restore physics
        return f"MIRACULUM! FLUXUS DIVINUS. IDENTITAS NUNC {core.identity_wave:.2f}"

    def _handle_anomalia(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        name = lit[0].upper() if lit else 'ENTROPIC_CASCADE'
        core.anomaly = name
        return f"ANOMALIA '{name}' INDUCTA EST IN '{self.focus}'."


# --- Main Execution & Testing Logic ---
def main():
    """Main function to run the AetherOS REPL."""
    context = Contextus()
    print("\n--- AetherOS v3.3 REPL ---")
    print("Type 'test' to run the unit tests, or 'vale' to quit.")
    
    while True:
        try:
            cmd = input(f"aetheros({context.focus})> ")
            if cmd.lower() in ['exit', 'vale']: break
            if not cmd.strip(): continue
            if cmd.lower() == 'test':
                run_tests()
                continue
            
            response = context.execute_command(cmd)
            print(f"< {response}")

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"< FATAL ERRORUM: {e}")
    
    print("\n< VALE.")

def run_tests():
    """Discovers and runs the unit tests."""
    print("\n--- Running AetherOS Test Suite ---")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAetherOS))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    print("--- Test Suite Complete ---\n")


class TestAetherOS(unittest.TestCase):
    """Unit tests for the AetherOS command handlers."""
    def setUp(self):
        """Set up a fresh context for each test."""
        # Suppress boot messages during tests
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        self.context = Contextus()
        sys.stdout.close()
        sys.stdout = original_stdout
        time.sleep(0.1) # Allow threads to start

    def test_creation_and_focus(self):
        self.context.execute_command("CREO 'TEST1'")
        self.assertIn('TEST1', self.context.materiae)
        self.assertEqual(self.context.focus, 'TEST1')
        self.context.execute_command("FOCUS 'GENESIS'")
        self.assertEqual(self.context.focus, 'GENESIS')

    def test_teach_learn_verbs(self):
        self.context.execute_command("CREO 'SAPIENTIA'")
        self.context.execute_command("FOCUS 'SAPIENTIA'")
        self.context.execute_command("PERTURBO 'This is the original wisdom.'")
        
        self.context.execute_command("CREO 'DISCIPULUS'")
        self.assertNotIn('SAPIENTIA_EX_SAPIENTIA', self.context.materiae['DISCIPULUS'].context_embeddings)

        # Test DOCEO
        self.context.execute_command("DOCEO 'DISCIPULUS' CUM 'SAPIENTIA'")
        self.assertIn('SAPIENTIA_EX_SAPIENTIA', self.context.materiae['DISCIPULUS'].context_embeddings)

        # Test DISCERE
        self.context.execute_command("FOCUS 'DISCIPULUS'")
        self.context.execute_command("DISCERE EX 'SAPIENTIA'")
        self.assertIn('SAPIENTIA_EX_SAPIENTIA', self.context.materiae['DISCIPULUS'].context_embeddings)

    def test_dialectica(self):
        self.context.execute_command("INSTAURO 'SOURCE'")
        self.assertIn('SOURCE', self.context.materiae)
        
        self.context.execute_command("DIALECTICA 'SOURCE' 'THESIS' 'ANTITHESIS'")
        self.assertNotIn('SOURCE', self.context.materiae)
        self.assertIn('THESIS', self.context.materiae)
        self.assertIn('ANTITHESIS', self.context.materiae)
        self.assertEqual(self.context.focus, 'THESIS')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':
        run_tests()
    else:
        main()
