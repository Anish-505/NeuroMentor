# File: /lstm-deep-learning-project/lstm-deep-learning-project/tests/test_data.py

import unittest
from src.data.loader import load_data
from src.data.preprocessing import minmax_scaling, create_sliding_windows
from src.data.datasets import TimeSeriesDataset

class TestDataFunctions(unittest.TestCase):
    def setUp(self):
        # This method will run before each test
        self.sample_data = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        self.scaled_data = minmax_scaling(self.sample_data)

    def test_load_data(self):
        # Test the load_data function to ensure it loads data correctly
        data = load_data('path/to/sample.csv')  # Replace with actual path
        self.assertIsNotNone(data)
        self.assertGreater(len(data), 0)

    def test_minmax_scaling(self):
        # Test the minmax_scaling function
        expected_scaled_data = [
            [0.0, 0.0, 0.0],
            [0.5, 0.5, 0.5],
            [1.0, 1.0, 1.0]
        ]
        self.assertEqual(self.scaled_data, expected_scaled_data)

    def test_create_sliding_windows(self):
        # Test the create_sliding_windows function
        windows = create_sliding_windows(self.sample_data, window_size=2)
        expected_windows = [
            [[1, 2, 3], [4, 5, 6]],
            [[4, 5, 6], [7, 8, 9]]
        ]
        self.assertEqual(windows, expected_windows)

    def test_time_series_dataset(self):
        # Test the TimeSeriesDataset class
        dataset = TimeSeriesDataset(self.sample_data, train_size=0.67)
        self.assertEqual(len(dataset.train_data), 2)
        self.assertEqual(len(dataset.test_data), 1)

if __name__ == '__main__':
    unittest.main()