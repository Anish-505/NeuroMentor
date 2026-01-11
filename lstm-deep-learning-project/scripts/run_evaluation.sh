#!/bin/bash

# This script is used to run the evaluation of the trained LSTM model.

# Activate the conda environment if needed
# conda activate your_environment_name

# Set the path to the Python script for evaluation
EVALUATION_SCRIPT="src/evaluation/evaluate.py"

# Run the evaluation script
python $EVALUATION_SCRIPT

# Print a message indicating that the evaluation is complete
echo "Model evaluation completed."