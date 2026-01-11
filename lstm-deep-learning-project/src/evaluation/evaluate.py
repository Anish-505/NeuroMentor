# File: /lstm-deep-learning-project/lstm-deep-learning-project/src/evaluation/evaluate.py

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained LSTM model on the test dataset.

    Parameters:
    model: The trained LSTM model to be evaluated.
    X_test: The input features for the test dataset.
    y_test: The true output values for the test dataset.

    Returns:
    metrics: A dictionary containing evaluation metrics RMSE and MAE.
    """
    # Make predictions using the trained model
    predictions = model.predict(X_test)

    # Calculate RMSE (Root Mean Squared Error)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Calculate MAE (Mean Absolute Error)
    mae = mean_absolute_error(y_test, predictions)

    # Create a dictionary to hold the metrics
    metrics = {
        'RMSE': rmse,
        'MAE': mae
    }

    return metrics

def print_evaluation_metrics(metrics):
    """
    Print the evaluation metrics.

    Parameters:
    metrics: A dictionary containing evaluation metrics RMSE and MAE.
    """
    print("Evaluation Metrics:")
    print(f"RMSE: {metrics['RMSE']:.4f}")
    print(f"MAE: {metrics['MAE']:.4f}")