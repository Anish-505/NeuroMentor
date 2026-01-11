# Contents of /lstm-deep-learning-project/lstm-deep-learning-project/src/inference/predict.py

import numpy as np
import pandas as pd
from keras.models import load_model
from src.data.preprocessing import create_sliding_windows

def make_predictions(model_path, input_data, window_size):
    """
    Load the trained LSTM model and make predictions on the input data.

    Parameters:
    model_path (str): Path to the trained LSTM model.
    input_data (pd.DataFrame): DataFrame containing the input data for predictions.
    window_size (int): The size of the sliding window used for creating input sequences.

    Returns:
    np.ndarray: Predicted values.
    """
    # Load the trained model from the specified path
    model = load_model(model_path)

    # Prepare the input data using sliding windows
    X = create_sliding_windows(input_data.values, window_size)

    # Make predictions using the loaded model
    predictions = model.predict(X)

    return predictions

def save_predictions(predictions, output_file):
    """
    Save the predictions to a CSV file.

    Parameters:
    predictions (np.ndarray): Array of predicted values.
    output_file (str): Path to the output CSV file.
    """
    # Convert predictions to a DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Predicted Values'])

    # Save the DataFrame to a CSV file
    predictions_df.to_csv(output_file, index=False)

# Example usage (uncomment to use):
# if __name__ == "__main__":
#     model_path = 'path/to/your/model.h5'
#     input_data = pd.read_csv('path/to/your/input_data.csv')
#     window_size = 10
#     predictions = make_predictions(model_path, input_data, window_size)
#     save_predictions(predictions, 'path/to/save/predictions.csv')