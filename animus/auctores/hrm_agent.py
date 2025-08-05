# hrm_agent.py
#
# In-house implementation of the Hierarchical Reasoning Model (HRM).
# Designed to be hardware-agnostic (CPU/GPU) from the ground up.

import torch
import torch.nn as nn

# --- Hardware-Agnostic Device Setup ---
# This is the first critical step to ensure portability.
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"HRM Agent: Using device '{device}'")


class HRM(nn.Module):
    """
    The Hierarchical Reasoning Model class.

    This model consists of two interdependent recurrent modules:
    1.  A high-level (slow) module for abstract planning.
    2.  A low-level (fast) module for detailed computation, guided
        by the high-level module.
    """

    def __init__(self, input_size, hidden_size, output_size, num_fast_steps=5):
        """
        Initializes the HRM.

        Args:
            input_size (int): The dimensionality of the input state.
            hidden_size (int): The size of the hidden state for both modules.
            output_size (int): The dimensionality of the final output.
            num_fast_steps (int): The number of computational steps the low-level
                                  module performs per high-level step.
        """
        super(HRM, self).__init__()
        self.hidden_size = hidden_size
        self.num_fast_steps = num_fast_steps

        # --- High-Level (Slow) Module ---
        # A single-layer LSTM that processes the input to form a "plan" or context.
        self.high_level_rnn = nn.LSTMCell(input_size, hidden_size)

        # --- Low-Level (Fast) Module ---
        # A single-layer LSTM that takes the original input AND the high-level
        # context to perform detailed, iterative computation.
        self.low_level_rnn = nn.LSTMCell(input_size + hidden_size, hidden_size)

        # --- Output Layer ---
        # A linear layer to map the final low-level hidden state to an output.
        self.output_layer = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        """
        Performs a single forward pass through the HRM.

        Args:
            x (torch.Tensor): The input tensor of shape (batch_size, input_size).

        Returns:
            torch.Tensor: The output tensor of shape (batch_size, output_size).
        """
        # Get the batch size from the input tensor
        batch_size = x.size(0)

        # Initialize hidden and cell states for both RNNs on the correct device
        h_high, c_high = (torch.zeros(batch_size, self.hidden_size).to(device),
                          torch.zeros(batch_size, self.hidden_size).to(device))
        
        h_low, c_low = (torch.zeros(batch_size, self.hidden_size).to(device),
                        torch.zeros(batch_size, self.hidden_size).to(device))

        # --- 1. High-Level "Planning" Step ---
        # The slow module runs once to generate the context for the fast module.
        h_high, c_high = self.high_level_rnn(x, (h_high, c_high))

        # --- 2. Low-Level "Computation" Steps ---
        # The fast module iterates multiple times, guided by the high-level plan.
        for _ in range(self.num_fast_steps):
            # The input to the low-level RNN is the original input `x` concatenated
            # with the hidden state `h_high` from the high-level planner.
            low_level_input = torch.cat((x, h_high), dim=1)
            h_low, c_low = self.low_level_rnn(low_level_input, (h_low, c_low))

        # --- 3. Final Output ---
        # The output is generated from the final hidden state of the fast module.
        output = self.output_layer(h_low)
        return output

# --- Example Usage & Verification ---
if __name__ == '__main__':
    print("\n--- Running a simple verification test ---")
    
    # Model parameters (example)
    INPUT_DIM = 10  # e.g., representing the state of a 3x3 grid + target
    HIDDEN_DIM = 32 # Internal processing dimension
    OUTPUT_DIM = 2  # e.g., representing an (x, y) move
    BATCH_SIZE = 4

    # 1. Instantiate the model
    model = HRM(input_size=INPUT_DIM, hidden_size=HIDDEN_DIM, output_size=OUTPUT_DIM)
    
    # 2. Move the model to the selected device (CRITICAL STEP)
    model.to(device)
    print(f"Model moved to '{device}'.")

    # 3. Create a dummy input tensor
    dummy_input = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # 4. Move the input tensor to the same device (CRITICAL STEP)
    dummy_input = dummy_input.to(device)
    print(f"Input tensor created on '{device}'.")

    # 5. Perform a forward pass
    try:
        output = model(dummy_input)
        print("Forward pass successful.")
        print(f"Output shape: {output.shape}") # Should be (BATCH_SIZE, OUTPUT_DIM)
        assert output.shape == (BATCH_SIZE, OUTPUT_DIM)
        print("Verification PASSED.")
    except Exception as e:
        print(f"Verification FAILED. Error: {e}")