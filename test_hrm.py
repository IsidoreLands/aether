# test_hrm.py
#
# A formal test suite for the HRM agent using Python's unittest framework.
# This script verifies the model's functionality and reproducibility.

import unittest
import torch

# Import the model and device configuration from our agent script
from hrm_agent import HRM, device

class TestHRM(unittest.TestCase):
    """
    Test case for the Hierarchical Reasoning Model.
    """

    def setUp(self):
        """
        This method is called before each test. It sets up a standard
        model instance for testing.
        """
        # Define a standard set of parameters for all tests
        self.input_dim = 10
        self.hidden_dim = 32
        self.output_dim = 2
        self.batch_size = 4

        # Instantiate the model and move it to the configured device
        self.model = HRM(
            input_size=self.input_dim,
            hidden_size=self.hidden_dim,
            output_size=self.output_dim
        ).to(device)

    def test_forward_pass_and_shape(self):
        """
        Tests if a forward pass can be completed without errors and
        if the output tensor has the correct shape.
        """
        # Create a dummy input tensor on the correct device
        dummy_input = torch.randn(self.batch_size, self.input_dim).to(device)
        
        # Perform the forward pass
        output = self.model(dummy_input)

        # Assert that the output shape is what we expect
        expected_shape = (self.batch_size, self.output_dim)
        self.assertEqual(output.shape, expected_shape)
        print(f"\n[Test Case] Forward Pass & Shape: PASSED")

    def test_reproducibility(self):
        """
        Tests if the model produces the exact same output for the same
        input when the random seed is fixed. This is crucial for debugging.
        """
        # Set a fixed seed for random number generators
        torch.manual_seed(42)
        
        # Create a dummy input tensor
        dummy_input = torch.randn(self.batch_size, self.input_dim).to(device)

        # Get the first output
        output1 = self.model(dummy_input)

        # Reset the seed and run again with the same input
        torch.manual_seed(42)
        output2 = self.model(dummy_input)

        # Assert that the two outputs are identical
        self.assertTrue(torch.equal(output1, output2))
        print(f"[Test Case] Reproducibility: PASSED")

# This allows running the tests directly from the command line
if __name__ == '__main__':
    unittest.main()