# train_hrm.py
#
# This script trains our in-house HRM model on a basic navigation task.
# The goal is to create a baseline trained model before introducing
# more complex scenarios like the local minima trap or the SAGA loop.

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# Import our model and device configuration
from animus.auctores.hrm_agent import HRM, device

# --- Environment & Data Generation ---

# A simplified version of the GridEnvironment for generating training data
GRID_SIZE = 11
TARGET_POS = (10, 10)

def state_to_tensor(position):
    """Converts a (row, col) position tuple into a tensor representation."""
    # Simple representation: [current_row, current_col, target_row, target_col]
    state_array = np.array([position[0], position[1], TARGET_POS[0], TARGET_POS[1]], dtype=np.float32)
    # Return as a batch of 1 on the correct device
    return torch.from_numpy(state_array).unsqueeze(0).to(device)

def generate_training_data(num_samples=500):
    """
    Generates expert training data. For each sample, it provides a random
    position and the optimal one-step move towards the target.
    """
    states = []
    labels = []
    for _ in range(num_samples):
        # Create a random position on the grid
        current_pos = (np.random.randint(0, GRID_SIZE), np.random.randint(0, GRID_SIZE))

        # Skip if already at the target
        if current_pos == TARGET_POS:
            continue

        # Calculate the optimal move (direction vector)
        delta_row = TARGET_POS[0] - current_pos[0]
        delta_col = TARGET_POS[1] - current_pos[1]
        
        # Normalize the vector to get a single step
        optimal_move = (np.sign(delta_row), np.sign(delta_col))
        
        # The state is the input, the move is the label (what we want to predict)
        states.append(state_to_tensor(current_pos))
        labels.append(torch.tensor(optimal_move, dtype=torch.float32).unsqueeze(0).to(device))
        
    return states, labels

# --- Training Loop ---

if __name__ == '__main__':
    # 1. Hyperparameters and Model Initialization
    INPUT_DIM = 4   # State: [cur_r, cur_c, tar_r, tar_c]
    HIDDEN_DIM = 64
    OUTPUT_DIM = 2  # Predicted move: [move_r, move_c]
    
    model = HRM(input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM).to(device)
    
    # Using Mean Squared Error loss because we are predicting a continuous vector
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # 2. Generate Training Data
    print("Generating training data...")
    train_states, train_labels = generate_training_data(num_samples=2000)
    print(f"{len(train_states)} training samples generated.")

    # 3. The Training Loop
    print("\nStarting training...")
    epochs = 100
    for epoch in range(epochs):
        total_loss = 0
        for i in range(len(train_states)):
            state = train_states[i]
            label = train_labels[i]

            # Standard PyTorch training steps
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

    # 4. Save the trained model
    torch.save(model.state_dict(), "hrm_baseline.pth")
    print("\nModel saved to 'hrm_baseline.pth'.")

    # 5. Simple Evaluation
    print("\n--- Simple Evaluation ---")
    # Let's see what the model predicts for a starting position
    start_pos = (0, 0)
    state_tensor = state_to_tensor(start_pos)
    
    # Set the model to evaluation mode
    model.eval()
    with torch.no_grad(): # We don't need to calculate gradients for inference
        predicted_move = model(state_tensor)
    
    # Interpret the output
    predicted_move = predicted_move.squeeze().cpu().numpy()
    # Round to the nearest integer to get a clear step direction
    final_move = tuple(np.round(predicted_move).astype(int))
    
    print(f"For starting position {start_pos}, the model predicts the move: {final_move}")
    print("The optimal move is (1, 1). The closer the prediction, the better the training.")
