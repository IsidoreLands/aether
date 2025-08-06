# animus/auctores/train_saga_aware_hrm.py
#
# Trains the definitive, SAGA-AWARE version of our HRM agent.
# It uses the full 14D state vector and a "neutral context" training strategy
# to create a model that is primed to learn from historical Sagas.

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

from animus.auctores.hrm_agent import HRM, device
from experiri.baseline_runner import FortifiedGridEnvironment


def generate_saga_aware_training_data(num_samples=5000):
    """
    Generates expert training data using the full 14D state vector,
    with a neutral saga context.
    """
    env = FortifiedGridEnvironment()
    states = []
    labels = []

    for _ in range(num_samples):
        current_pos = (np.random.randint(0, env.size), np.random.randint(0, env.size))
        while current_pos in env.wall:
            current_pos = (
                np.random.randint(0, env.size),
                np.random.randint(0, env.size),
            )

        if current_pos == env.target:
            continue

        # --- CRITICAL CHANGE: Use a neutral context for baseline training ---
        # This teaches the model a strong default instinct.
        mock_saga_embedding = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        # --- Standard 10D state components ---
        local_walls = env.get_local_env_state(current_pos)
        status_vec = [1.0, 0.0]  # Assume last move was valid for expert data

        base_state_array = np.array(
            [*current_pos, *env.target, *local_walls, *status_vec], dtype=np.float32
        )

        # --- Assemble the full 14D state vector ---
        full_state_array = np.concatenate([base_state_array, mock_saga_embedding])

        # Calculate the optimal move (the label)
        delta_row = env.target[0] - current_pos[0]
        delta_col = env.target[1] - current_pos[1]
        optimal_move = (np.sign(delta_row), np.sign(delta_col))

        states.append(torch.from_numpy(full_state_array).unsqueeze(0).to(device))
        labels.append(
            torch.tensor(optimal_move, dtype=torch.float32).unsqueeze(0).to(device)
        )

    return states, labels


if __name__ == "__main__":
    # Define the new, larger SAGA-AWARE architecture
    INPUT_DIM = 14
    HIDDEN_DIM = 128  # Increased model capacity
    OUTPUT_DIM = 2

    model = HRM(
        input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM
    ).to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("Generating Saga-Aware training data (14D state, Neutral Context)...")
    train_states, train_labels = generate_saga_aware_training_data()
    print(f"{len(train_states)} training samples generated.")

    # Training Loop
    print("\nStarting training for the Saga-Aware HRM...")
    epochs = 200  # Increased training duration
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
            avg_loss = total_loss / len(train_states)
            print(f"Epoch [{epoch+1}/{epochs}], Average Loss: {avg_loss:.6f}")

    print("Training complete.")

    output_path = "models/hrm_checkpoints/hrm_saga_aware.pth"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(model.state_dict(), output_path)
    print(f"\nModel saved to '{output_path}'.")
    print("This model is now ready for the SAGA learning loop.")
