# animus/auctores/train_arc_gnosis.py
# Trains the ARC agent on the "Gnosis" curriculum, a mix of direct-path
# "instinct" data and obstacle-avoidance "insight" data.

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import sys
from sentence_transformers import SentenceTransformer

# Add project root to path to find modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from animus.auctores.hrm_agent import HRM, device
from experiri.baseline_runner import FortifiedGridEnvironment

# --- Load the embedding model ---
embedding_model = SentenceTransformer('models/all-MiniLM-L6-v2', device=device)
EMBEDDING_DIM = embedding_model.get_sentence_embedding_dimension()
SEXTET_DIM = 6

def get_gnosis_move(pos, target, wall):
    """A simple pathfinding heuristic to find the correct first move around an obstacle."""
    # Try direct move first
    delta = (np.sign(target[0] - pos[0]), np.sign(target[1] - pos[1]))
    next_pos = (pos[0] + delta[0], pos[1] + delta[1])
    if next_pos not in wall:
        return delta

    # Try moving perpendicular to the wall (assuming a simple vertical or horizontal wall)
    if pos[0] == wall[0][0]: # Vertical wall
        if (pos[0], pos[1] - 1) not in wall: return (0, -1)
        if (pos[0], pos[1] + 1) not in wall: return (0, 1)
    if pos[1] == wall[0][1]: # Horizontal wall
        if (pos[0] - 1, pos[1]) not in wall: return (-1, 0)
        if (pos[0] + 1, pos[1]) not in wall: return (1, 0)

    return (0, 0) # Fallback if completely boxed in

def generate_gnosis_training_data(num_samples=10000):
    env = FortifiedGridEnvironment()
    states, labels = [], []
    
    neutral_saga_text = "A new journey begins without any prior history."
    neutral_embedding = embedding_model.encode(neutral_saga_text, convert_to_tensor=True).cpu()

    for i in range(num_samples):
        current_pos = tuple(np.random.randint(0, env.size, 2))
        while current_pos in env.wall or current_pos == env.target:
            current_pos = tuple(np.random.randint(0, env.size, 2))

        temp_wall = []
        # --- The Gnosis / Instinct curriculum split ---
        if np.random.rand() > 0.80: # 20% Gnosis Data
            # Create a small procedural wall
            wall_len = 3
            if np.random.rand() > 0.5: # Vertical wall
                wall_x = np.random.randint(1, env.size-1)
                wall_y_start = np.random.randint(0, env.size - wall_len)
                temp_wall = [(wall_x, y) for y in range(wall_y_start, wall_y_start + wall_len)]
            else: # Horizontal wall
                wall_y = np.random.randint(1, env.size-1)
                wall_x_start = np.random.randint(0, env.size - wall_len)
                temp_wall = [(x, wall_y) for x in range(wall_x_start, wall_x_start + wall_len)]
            
            # Find the correct move using the heuristic
            optimal_move = get_gnosis_move(current_pos, env.target, temp_wall)
        else: # 80% Instinct Data
            optimal_move = (np.sign(env.target[0] - current_pos[0]), np.sign(env.target[1] - current_pos[1]))

        # Get local wall data (combining permanent and temporary walls)
        full_wall = env.wall + temp_wall
        local_walls = [1.0 if (current_pos[0]+dx, current_pos[1]+dy) in full_wall else 0.0 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]]

        # Assemble the full state tensor
        status_vec = [1.0, 0.0]
        neutral_sextet_array = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 0.0])
        base_state_array = np.array([*current_pos, *env.target, *local_walls, *status_vec])
        
        full_state_tensor = torch.cat([
            torch.from_numpy(base_state_array),
            neutral_embedding,
            torch.from_numpy(neutral_sextet_array)
        ]).to(torch.float32).unsqueeze(0).to(device)
        
        states.append(full_state_tensor)
        labels.append(torch.tensor(optimal_move, dtype=torch.float32).unsqueeze(0).to(device))
        
    return states, labels

if __name__ == '__main__':
    INPUT_DIM = 10 + EMBEDDING_DIM + SEXTET_DIM # 400
    HIDDEN_DIM = 384
    OUTPUT_DIM = 2
    
    model = HRM(input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM).to(device)
    criterion, optimizer = nn.MSELoss(), optim.Adam(model.parameters(), lr=0.0005)

    print(f"Generating Gnosis training data ({INPUT_DIM}D state)...")
    train_states, train_labels = generate_gnosis_training_data()
    print(f"{len(train_states)} samples generated.")

    print("\nStarting Gnosis training for ARC...")
    epochs = 300 # More epochs for the more complex curriculum
    for epoch in range(epochs):
        total_loss = 0
        for state, label in zip(train_states, train_labels):
            optimizer.zero_grad()
            output = model(state)
            loss = criterion(output, label)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss / len(train_states):.6f}")

    print("Training complete.")
    output_path = "models/hrm_checkpoints/ARC_Gnosis.pth"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(model.state_dict(), output_path)
    print(f"\nModel saved to '{output_path}'.")
