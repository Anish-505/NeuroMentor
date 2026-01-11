# File: /lstm-deep-learning-project/lstm-deep-learning-project/src/data/loader.py

import pandas as pd
import os

def load_data(file_path):
    """
    Load dataset from a specified file path.
    
    Parameters:
    file_path (str): The path to the dataset file (CSV format).
    
    Returns:
    DataFrame: A pandas DataFrame containing the loaded data.
    
    Raises:
    FileNotFoundError: If the specified file does not exist.
    ValueError: If the file format is not supported.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    # Load the data based on the file extension
    file_extension = os.path.splitext(file_path)[1]
    
    if file_extension == '.csv':
        data = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please use a CSV file.")
    
    return data

def load_multiple_files(file_paths):
    """
    Load multiple datasets from a list of file paths.
    
    Parameters:
    file_paths (list): A list of paths to the dataset files (CSV format).
    
    Returns:
    DataFrame: A pandas DataFrame containing the concatenated data from all files.
    """
    data_frames = []
    
    for file_path in file_paths:
        try:
            data = load_data(file_path)
            data_frames.append(data)
        except (FileNotFoundError, ValueError) as e:
            print(e)
    
    # Concatenate all data frames into a single data frame
    return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()