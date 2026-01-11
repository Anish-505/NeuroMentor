def minmax_scaling(data):
    """
    Scales the input data to a range between 0 and 1 using Min-Max scaling.
    
    Parameters:
    data (numpy.ndarray): The input data to be scaled.
    
    Returns:
    numpy.ndarray: Scaled data.
    """
    min_val = data.min(axis=0)
    max_val = data.max(axis=0)
    scaled_data = (data - min_val) / (max_val - min_val)
    return scaled_data


def create_sliding_windows(data, window_size):
    """
    Creates sliding windows from the input data for time series forecasting.
    
    Parameters:
    data (numpy.ndarray): The input data to create windows from.
    window_size (int): The size of each sliding window.
    
    Returns:
    tuple: A tuple containing the input windows and the corresponding target values.
    """
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size])
    return np.array(X), np.array(y)