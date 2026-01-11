import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === USER: Set the path to your saved CSV file ===
CSV_FILE = r"C:/Users/ankit/OneDrive/Documents/Personal/Repls/Complete code/Random Python/NeuroMentor/Resource files/EEG_Dataset_Faizan.csv" # << Set your custom save path here
 
# === Read the CSV file into a Pandas DataFrame ===
# The new Arduino code produces a clean CSV, so we can read it directly.
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    print(f"[ERROR] File not found at: {CSV_FILE}")
    print("Please make sure the path is correct and you have downloaded the data.")
    exit()

print("--- Data Head (First 5 Rows) ---")
print(df.head())
print("\n--- Data Info ---")
df.info()

# === Separate data by state for plotting ===
baseline_df = df[df['State'] == 'Baseline']
stressed_df = df[df['State'] == 'Stressed']
focused_df = df[df['State'] == 'Focused']

# List of brainwave columns to plot
brainwave_columns = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']

# === Create the Plot ===
fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True, sharey=True)
fig.suptitle('EEG Band Power Across Different States', fontsize=16)

# Plot for Baseline
for column in brainwave_columns:
    axes[0].plot(baseline_df[column].values, label=column)
axes[0].set_title('Baseline State')
axes[0].grid(True, linestyle='--', alpha=0.6)
axes[0].legend()
axes[0].set_ylabel('Magnitude')


# Plot for Stressed
for column in brainwave_columns:
    axes[1].plot(stressed_df[column].values, label=column)
axes[1].set_title('Stressed State')
axes[1].grid(True, linestyle='--', alpha=0.6)
axes[1].legend()
axes[1].set_ylabel('Magnitude')


# Plot for Focused
for column in brainwave_columns:
    axes[2].plot(focused_df[column].values, label=column)
axes[2].set_title('Focused State')
axes[2].grid(True, linestyle='--', alpha=0.6)
axes[2].legend()
axes[2].set_ylabel('Magnitude')


plt.xlabel('Time (Number of Readings per State)')
plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Adjust layout to make room for suptitle
plt.show()
