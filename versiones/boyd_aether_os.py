#!/usr/bin/env python3

import os
import re
import sys
import threading
import time
import random
import numpy as np
import asyncio
import aiohttp

# Import Boyd-specific physics and the new universal model loader
from versiones.boyd_flux_core import FluxCore, Intellectus
from experiri.model_loader import load_player

# --- OODA Loop & E-M Grammar ---
KNOWN_VERBS = ['ENGAGE', 'DISENGAGE', 'CREATE', 'STATUS', 'FOCUS', 'JAM', 'INTERROGATE']
KNOWN_MODIFIERS = ['AGGRESSIVE', 'DEFENSIVE', 'NEUTRAL', 'IMMEDIATE']
modifier_map = {
    'NEUTRAL': {'thrust_mod': 1.0, 'load_mod': 1.0},
    'AGGRESSIVE': {'thrust_mod': 1.5, 'load_mod': 1.2},
    'DEFENSIVE': {'thrust_mod': 0.8, 'load_mod': 1.8},
    'IMMEDIATE': {'thrust_mod': 2.0, 'load_mod': 0.5} # High thrust, low load for quick reaction
}
PHI = (1 + np.sqrt(5)) / 2

def text_to_amp(text):
    """Convert text to amplitude by summing ord values and taking log1p."""
    return np.log1p(sum(ord(c) for c in text))

# --- Main Application Context and Executor ---
class Contextus:
    """The cockpit and battle management system for an E-M agent."""
    def __init__(self):
        self.squadron = {} # Renamed from 'materiae'
        self.target = None # Renamed from 'focus'
        self.lock = threading.RLock()
        self.verb_handlers = self._get_verb_handlers()
        self._boot()
        # No autonomous regulator for the Boyd version; all actions are deliberate.

    def _boot(self):
        """Initialize the lead agent."""
        print("< E-M Combat System v4.1 (OODA) Initializing... >")
        lead_agent = FluxCore()
        self.squadron['LEAD'] = lead_agent
        self.target = 'LEAD'
        lead_agent.maneuver(10, 0.1)
        print("< Lead agent online. Target lock on 'LEAD'. >")

    def get_targeted_agent(self):
        """Get the currently targeted agent."""
        with self.lock:
            if not self.target or self.target not in self.squadron:
                self.target = 'LEAD' if 'LEAD' in self.squadron else None
            if not self.target: raise ValueError("NO AGENT TARGETED")
            return self.squadron[self.target]

    async def execute_command(self, cmd):
        """Execute a combat directive."""
        try:
            verb, modifier, literals, args_str = self._parse_command(cmd)
            mods = modifier_map.get(modifier, {'thrust_mod': 1.0, 'load_mod': 1.0})
            
            handler = self.verb_handlers.get(verb)
            if handler:
                if asyncio.iscoroutinefunction(handler):
                    return await handler(modifier, mods, literals, args_str)
                else:
                    return handler(modifier, mods, literals, args_str)
            return f"DIRECTIVE UNKNOWN: '{verb}'"
        except Exception as e:
            return f"SYSTEM FAULT: {e}"

    def _parse_command(self, cmd):
        """Parse the command into verb, modifier, and literals."""
        match = re.match(r"([A-Z]+)(?:\s+([A-Z]+))?\s*(.*)", cmd.strip().upper())
        if not match: raise ValueError("INVALID DIRECTIVE FORMAT")
        verb, modifier, args_str = match.groups()
        
        if verb not in KNOWN_VERBS: raise ValueError(f"UNKNOWN VERB: {verb}")
        if modifier and modifier not in KNOWN_MODIFIERS:
            # If the second word is not a known modifier, it's part of the args
            args_str = f"{modifier} {args_str}".strip()
            modifier = 'NEUTRAL'

        literals = re.findall(r"'([^']*)'", args_str)
        return verb, modifier or 'NEUTRAL', literals, args_str

    def _get_verb_handlers(self):
        """Map combat verbs to handlers."""
        return {
            'CREATE': self._handle_create, 'FOCUS': self._handle_focus,
            'STATUS': self._handle_status, 'ENGAGE': self._handle_engage,
            'DISENGAGE': self._handle_disengage, 'INTERROGATE': self._handle_interrogate
        }

    # --- Verb Handlers (The "Act" part of OODA) ---
    def _handle_create(self, mod, mods, lit, args):
        """Create a new agent in the squadron."""
        callsign = lit[0].upper() if lit else "WINGMAN"
        if callsign in self.squadron: return f"CALLSIGN '{callsign}' ALREADY IN USE."
        self.squadron[callsign] = FluxCore()
        self.target = callsign
        return f"AGENT '{callsign}' ADDED TO SQUADRON."

    def _handle_focus(self, mod, mods, lit, args):
        """Change target lock to another agent."""
        callsign = lit[0].upper()
        if callsign not in self.squadron: return f"AGENT '{callsign}' NOT FOUND."
        self.target = callsign
        return f"TARGET LOCK ON '{callsign}'."

    def _handle_status(self, mod, mods, lit, args):
        """Report the status of an agent."""
        agent_to_report = lit[0].upper() if lit else self.target
        if agent_to_report not in self.squadron: return f"AGENT '{agent_to_report}' NOT FOUND."
        return self.squadron[agent_to_report].display()

    def _handle_engage(self, mod, mods, lit, args):
        """Command an agent to perform an offensive maneuver."""
        agent = self.get_targeted_agent()
        amp = text_to_amp(lit[0]) if lit else 10.0
        thrust_change = amp * 0.1 * mods['thrust_mod']
        load_factor_change = amp * 0.01 * mods['load_mod']
        agent.maneuver(thrust_change, load_factor_change)
        return f"ENGAGING. Es={agent.specific_energy:.2f}"

    def _handle_disengage(self, mod, mods, lit, args):
        """Command an agent to perform a stabilizing/defensive maneuver."""
        agent = self.get_targeted_agent()
        agent.stabilize()
        return f"DISENGAGING. Es={agent.specific_energy:.2f}"

    async def _handle_interrogate(self, mod, mods, lit, args):
        """Query intel for a tactical update (Orient/Decide)."""
        agent = self.get_targeted_agent()
        model_key = (re.search(r"INTEL\s+'([^']*)'", args.upper()) or [None, 'ollama_phi3'])[1]

        try:
            player = load_player(model_key)
        except Exception as e:
            return f"INTEL FAILURE: Could not load model '{model_key}'. {e}"

        prompt = lit[0] if lit else "Assess current energy state and recommend next maneuver."
        
        async with aiohttp.ClientSession() as session:
            response_data = await player.get_response(prompt, session)
        
        if "error" in response_data:
            return f"INTEL FAILURE: {response_data['error']}"

        response_text = response_data.get('response', str(response_data))
        amp = text_to_amp(response_text)
        
        # Act on the intel immediately
        agent.maneuver(amp * 0.2 * mods['thrust_mod'], amp * 0.02 * mods['load_mod'])
        agent.context_embeddings['LATEST_INTEL'] = response_text
        return f"INTEL RECEIVED. MANEUVERING BASED ON NEW DATA."

# --- Main Execution Logic ---
async def main():
    context = Contextus()
    print("\n--- AetherOS E-M REPL ---")
    print("Directives: CREATE, FOCUS, STATUS, ENGAGE, DISENGAGE, INTERROGATE")
    print("Modifiers: AGGRESSIVE, DEFENSIVE, NEUTRAL, IMMEDIATE")
    print("Example: ENGAGE AGGRESSIVE 'BREAK RIGHT'")
    print("Type 'vale' to exit.")
    
    while True:
        try:
            cmd = await asyncio.to_thread(input, f"aetheros({context.target})> ")
            if cmd.lower() in ['exit', 'vale']: break
            if not cmd.strip(): continue
            response = await context.execute_command(cmd)
            print(f"< {response}")
        except (EOFError, KeyboardInterrupt):
            break
    print("\n< SIMULATOR OFFLINE.")

if __name__ == '__main__':
    asyncio.run(main())
