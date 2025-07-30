# boyd_aether_os.py
#
# Description:
# An alternative AetherOS runtime that uses the Energy-Maneuverability
# physics model defined in boyd_flux_core.py.

import os
import re
import sys
import threading
import time
import random
import numpy as np
import unittest

# Import components from the E-M modules
from boyd_flux_core import FluxCore, Intellectus
from oracle import get_oracle

# --- AetherOS Grammar and Constants (mostly unchanged) ---
KNOWN_VERBS = ['PERTURBO', 'CONVERGO', 'CREO', 'OSTENDO', 'FOCUS', 'ANOMALIA', 'VERITAS', 
               'MIRACULUM', 'REDIMO', 'INTERROGO', 'INSTAURO', 'EXERCEO', 'DIALECTICA', 
               'DOCEO', 'DISCERE']
KNOWN_INFLECTIONS = ['ABAM', 'EBAM', 'AM', 'O', 'E']
inflection_map = {
    'O': {'mod': 1.0}, 'E': {'mod': -1.0}, 'ABAM': {'mod': 1.5},
    'EBAM': {'mod': -0.5}, 'AM': {'mod': random.uniform(0.5, 1.5)}
}
PHI = (1 + np.sqrt(5)) / 2

# Helper functions (text_to_amp, etc.) remain the same...
def text_to_amp(text):
    return np.log1p(sum(ord(c) for c in text))

# --- Main Application Context and Executor ---
class Contextus:
    """The container for the entire AetherOS cosmos and command execution."""
    def __init__(self):
        self.materiae = {}
        self.focus = None
        self.lock = threading.RLock()
        self.verb_handlers = self._get_verb_handlers()
        self._boot()
        # FIX: The DialecticRegulator does not exist in this version and has been removed.

    def _boot(self):
        print("< AetherOS v3.3 E-M (Boyd) Initializing... >")
        g = FluxCore()
        self.materiae['GENESIS'] = g
        self.focus = 'GENESIS'
        g.maneuver(10, 0.1)
        print("< Genesis Rhythm Complete. Focus on 'GENESIS'. >")

    def get_focused_materia(self):
        with self.lock:
            if not self.focus or self.focus not in self.materiae:
                self.focus = 'GENESIS' if 'GENESIS' in self.materiae else None
            if not self.focus: raise ValueError("NULLA MATERIA IN FOCO EST")
            return self.materiae[self.focus]

    def execute_command(self, cmd):
        try:
            verb, inflection, literals, args_str = self._parse_latin_command(cmd)
            mod = inflection_map.get(inflection, {'mod': 1.0})['mod']
            handler = self.verb_handlers.get(verb)
            if handler:
                return handler(inflection, mod, literals, args_str)
            return f"VERBUM IGNORATUM '{verb}'"
        except Exception as e:
            return f"ERRORUM INTERNUM: {e}"

    def _parse_latin_command(self, cmd):
        match = re.match(r"([A-Z]+(?:O|E|ABAM|EBAM|AM)?)\s*(.*)", cmd.strip().upper())
        if not match: raise ValueError("FORMATUM INVALIDUM")
        verb_full, args_str = match.groups()
        verb, inflection = verb_full, 'O'
        for v in KNOWN_VERBS:
            if verb_full.startswith(v):
                verb, inflection = v, verb_full[len(v):] or 'O'
                break
        literals = re.findall(r"'([^']*)'", args_str)
        return verb, inflection, literals, args_str

    def _get_verb_handlers(self):
        return {
            'CREO': self._handle_creo, 'INSTAURO': self._handle_instauro,
            'FOCUS': self._handle_focus, 'OSTENDO': self._handle_ostendo,
            'PERTURBO': self._handle_perturbo, 'CONVERGO': self._handle_convergo,
            'INTERROGO': self._handle_interrogo,
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
        amp = text_to_amp(lit[0]) if lit else 10.0
        thrust_change = amp * 0.1 * mod
        load_factor_change = amp * 0.01 * mod
        core.maneuver(thrust_change, load_factor_change)
        return f"MANEUVER COMPLETE. Es={core.specific_energy:.2f}"

    def _handle_convergo(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        core.stabilize()
        return f"STABILIZING. Es={core.specific_energy:.2f}"

    def _handle_interrogo(self, inf, mod, lit, args):
        core = self.get_focused_materia()
        model_name = (re.search(r"ORACULO\s+'([^']*)'", args.upper()) or [None, 'gemini-1.5-flash'])[1]
        oracle = get_oracle(model_name)
        prompt = lit[0] if lit else "Describe your current energy state."
        response = oracle.query(prompt)
        
        amp = text_to_amp(response)
        core.maneuver(amp * 0.2, amp * 0.02)
        core.context_embeddings['ORACULUM_RESPONSUM'] = response
        return f"ORACULUM RESPONDIT. MANEUVER INITIATED."

# --- Main Execution Logic ---
def main():
    context = Contextus()
    print("\n--- AetherOS E-M REPL ---")
    print("Type 'vale' to quit.")
    while True:
        try:
            cmd = input(f"aetheros({context.focus})> ")
            if cmd.lower() in ['exit', 'vale']: break
            if not cmd.strip(): continue
            response = context.execute_command(cmd)
            print(f"< {response}")
        except (EOFError, KeyboardInterrupt):
            break
    print("\n< VALE.")

if __name__ == '__main__':
    main()
