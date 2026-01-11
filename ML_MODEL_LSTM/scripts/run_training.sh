#!/bin/bash

# This script is used to run the training process for the LSTM model.

# Activate the conda environment if using conda
# conda activate your_environment_name

# Set the Python path to the src directory
export PYTHONPATH=$(pwd)/src

# Run the training script
python -m training.train

# Note: Ensure that the necessary configurations are set in config.yaml before running the training.