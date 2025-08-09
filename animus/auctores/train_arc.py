# animus/auctores/train_arc.py
# Trains the final ARC (Animus Recurrens Cogitans) agent.

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

def generate_arc_training_data(num_samples=5000):
    env = FortifiedGridEnvironment()
    states, labels = [], []
    neutral_saga_text = "A new journey begins without any prior history."
    neutral_embedding = embedding_model.encode(neutral_saga_text, convert_to_tensor=True).cpu()
    for _ in range(num_samples):
        current_pos = tuple(np.random.randint(0, env.size, 2))
        while current_pos in env.wall or current_pos == env.target:
            current_pos = tuple(np.random.randint(0, env.size, 2))
        
        base_state_array = np.array([*current_pos, *env.target, *env.get_local_env_state(current_pos), 1.0, 0.0])
        neutral_sextet_array = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 0.0])
        
        full_state_tensor = torch.cat([
            torch.from_numpy(base_state_array),
            neutral_embedding,
            torch.from_numpy(neutral_sextet_array)
        ]).to(torch.float32).unsqueeze(0).to(device)
        states.append(full_state_tensor)
        
        optimal_move = (np.sign(env.target[0] - current_pos[0]), np.sign(env.target[1] - current_pos[1]))
        labels.append(torch.tensor(optimal_move, dtype=torch.float32).unsqueeze(0).to(device))
    return states, labels

if __name__ == '__main__':
    INPUT_DIM = 10 + EMBEDDING_DIM + SEXTET_DIM
    HIDDEN_DIM = 384
    OUTPUT_DIM = 2
    
    model = HRM(input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM).to(device)
    criterion, optimizer = nn.MSELoss(), optim.Adam(model.parameters(), lr=0.0005)

    print(f"Generating ARC training data ({INPUT_DIM}D state)...")
    train_states, train_labels = generate_arc_training_data()
    print(f"{len(train_states)} samples generated.")

    print("\nStarting ARC training...")
    epochs = 250
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
    output_path = "models/hrm_checkpoints/ARC.pth"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(model.state_dict(), output_path)
    print(f"\nModel saved to '{output_path}'.")
