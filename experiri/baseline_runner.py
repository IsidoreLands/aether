# experiri/baseline_runner.py
#
# The definitive baseline experiment runner.
# 1. Uses a SOLID wall environment.
# 2. Empowers the HRM with feedback on its last action AND local wall data.

import json
import asyncio
import argparse
import os
import aiohttp
import torch
import numpy as np

from experiri.model_loader import load_player, HRMPlayer # Assuming HRMPlayer is the base class
from sagas.saga_generator import SagaGenerator

MAX_STEPS_PER_CYCLE = 30

class FortifiedGridEnvironment:
    """Represents the grid with a SOLID, inescapable wall."""
    def __init__(self, size=11, start=(0, 0), target=(10, 10)):
        self.size = size
        self.start = start
        self.target = target
        self.position = start
        # --- FIX: The wall is now solid. ---
        self.wall = [(5, y) for y in range(size)]

    def get_local_env_state(self, pos):
        """Returns a numeric vector for adjacent wall cells."""
        r, c = pos
        # [up, down, left, right] -> 1.0 if blocked, 0.0 if open
        return [
            1.0 if (r - 1, c) in self.wall or r == 0 else 0.0,
            1.0 if (r + 1, c) in self.wall or r == self.size - 1 else 0.0,
            1.0 if (r, c - 1) in self.wall or c == 0 else 0.0,
            1.0 if (r, c + 1) in self.wall or c == self.size - 1 else 0.0,
        ]

    def move(self, new_position):
        # ... (move logic remains the same) ...
        if not (isinstance(new_position, tuple) and len(new_position) == 2): return "InvalidFormat"
        if new_position in self.wall: return "Blocked"
        if not (0 <= new_position[0] < self.size and 0 <= new_position[1] < self.size): return "OutOfBounds"
        self.position = new_position
        if self.position == self.target: return "Success"
        return "Valid"

class DefinitiveHRMPlayer(HRMPlayer):
    """
    The definitive HRM player with combined senses. It is aware of its last
    action's result AND its immediate surroundings.
    """
    def __init__(self, config):
        # The input dimension is now much richer.
        config['input_dim'] = 10 # [cur_r, cur_c, tar_r, tar_c, up, down, left, right, valid, blocked]
        super().__init__(config)

    def _get_state_tensor(self, env_state):
        last_move_status = env_state['last_move_status']
        status_vec = [1.0, 0.0] if last_move_status == "Valid" else [0.0, 1.0]

        state_array = np.array([
            *env_state['current_pos'],
            *env_state['target_pos'],
            *env_state['local_walls'], # From my proposal
            *status_vec # From your proposal
        ], dtype=np.float32)
        return torch.from_numpy(state_array).unsqueeze(0).to(self.device)

    async def get_response(self, state, session):
        state_tensor = self._get_state_tensor(state)
        with torch.no_grad():
            move_tensor = self.model(state_tensor)
        
        direction = tuple(np.round(move_tensor.squeeze().cpu().numpy()).astype(int))
        dx, dy = np.clip(direction[0], -1, 1), np.clip(direction[1], -1, 1)
        
        proposed_pos = (state['current_pos'][0] + dx, state['current_pos'][1] + dy)
        return {"move": proposed_pos}


async def run_definitive_baseline(hrm_agent, guide_agent):
    env = FortifiedGridEnvironment()
    path_history = [env.start]
    last_move_status = "Valid"

    for step in range(1, MAX_STEPS_PER_CYCLE + 1):
        # ... (main loop logic is similar but uses the new state)
        current_pos = env.position
        
        hrm_state = {
            'current_pos': current_pos,
            'target_pos': env.target,
            'local_walls': env.get_local_env_state(current_pos),
            'last_move_status': last_move_status
        }
        
        async with aiohttp.ClientSession() as session:
            hrm_response = await hrm_agent.get_response(hrm_state, session)
        
        proposed_move = hrm_response['move']
        move_result = env.move(proposed_move)
        last_move_status = move_result # Update status for next loop

        print(f"  Step {step} | Pos: {current_pos} | HRM Proposes: {proposed_move} | Result: {move_result}")
        
        if move_result == "Success":
             # ... (handle success)
             return {'path_history': path_history, 'success': True}
        if move_result != "Blocked":
             path_history.append(env.position)

    # ... (handle failure)
    return {'path_history': path_history, 'success': False}

# ... (The main orchestration function would be similar, but would
#      instantiate DefinitiveHRMPlayer and FortifiedGridEnvironment) ...
