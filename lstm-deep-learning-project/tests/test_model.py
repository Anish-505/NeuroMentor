# File: /lstm-deep-learning-project/lstm-deep-learning-project/tests/test_model.py

import unittest
from src.models.lstm_model import create_lstm_model
import numpy as np
from tensorflow.keras.models import Model

class TestLSTMModel(unittest.TestCase):
    def setUp(self):
        # Set up parameters for the LSTM model
        self.input_shape = (10, 1)  # Example input shape (timesteps, features)
        self.output_units = 1  # Number of output units
        self.model = create_lstm_model(self.input_shape, self.output_units)

    def test_model_structure(self):
        # Test if the model is an instance of Model
        self.assertIsInstance(self.model, Model)

    def test_model_output_shape(self):
        # Test if the output shape of the model is as expected
        test_input = np.random.rand(1, *self.input_shape)  # Random input for testing
        output = self.model.predict(test_input)
        self.assertEqual(output.shape, (1, self.output_units))

    def test_model_compile(self):
        # Test if the model compiles without errors
        try:
            self.model.compile(optimizer='adam', loss='mean_squared_error')
        except Exception as e:
            self.fail(f"Model compilation failed with error: {e}")

if __name__ == '__main__':
    unittest.main()