# train_definitive_hrm.py
#
# This script trains the DEFINITIVE version of our HRM agent.
# It uses the fortified environment and the full 10-dimensional state vector,
# creating a model compatible with our baseline_runner.py script.

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

# Import our model class and device configuration
from animus.auctores.hrm_agent import HRM, device

# Import the environment from our baseline runner to ensure consistency
from experiri.baseline_runner import FortifiedGridEnvironment


def generate_definitive_training_data(num_samples=5000):
    """
    Generates expert training data using the full 10D state vector.
    """
    env = FortifiedGridEnvironment()
    states = []
    labels = []

    for _ in range(num_samples):
        # Create a random position, but avoid placing it directly on the wall
        current_pos = (np.random.randint(0, env.size), np.random.randint(0, env.size))
        while current_pos in env.wall:
            current_pos = (
                np.random.randint(0, env.size),
                np.random.randint(0, env.size),
            )

        if current_pos == env.target:
            continue

        # Get local wall data
        local_walls = env.get_local_env_state(current_pos)

        # For expert data, the last move was always "Valid"
        status_vec = [1.0, 0.0]

        # Assemble the full 10D state vector
        state_array = np.array(
            [*current_pos, *env.target, *local_walls, *status_vec], dtype=np.float32
        )

        # Calculate the optimal move (the label)
        delta_row = env.target[0] - current_pos[0]
        delta_col = env.target[1] - current_pos[1]
        optimal_move = (np.sign(delta_row), np.sign(delta_col))

        states.append(torch.from_numpy(state_array).unsqueeze(0).to(device))
        labels.append(
            torch.tensor(optimal_move, dtype=torch.float32).unsqueeze(0).to(device)
        )

    return states, labels


if __name__ == "__main__":
    # Define the new, correct architecture
    INPUT_DIM = 10
    HIDDEN_DIM = 64  # This can be tuned
    OUTPUT_DIM = 2

    model = HRM(
        input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM
    ).to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Generate data with the new 10D state
    print("Generating definitive training data (10D state)...")
    train_states, train_labels = generate_definitive_training_data()
    print(f"{len(train_states)} training samples generated.")

    # Training Loop
    print("\nStarting training for the definitive HRM...")
    epochs = 150  # A few more epochs might be needed for the more complex state
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

    # Save the new, compatible model weights
    output_path = "models/hrm_checkpoints/hrm_definitive_baseline.pth"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(model.state_dict(), output_path)
    print(f"\nModel saved to '{output_path}'.")
    print("This model is now compatible with baseline_runner.py.")
