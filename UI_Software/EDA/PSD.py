import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === USER SETTINGS ===
# Use the same path as your other scripts.
CSV_FILE = r"C:/Users/ankit/OneDrive/Documents/Personal/Repls/Complete code/Random Python/NeuroMentor/Resource files/EEG_Dataset_Faizan.csv"

def plot_psd(df):
    """
    Calculates and plots the average Power Spectral Density for each state.

    Args:
        df (pd.DataFrame): The dataframe containing the full EEG dataset.
    """
    # Use a nice plot style
    sns.set_style("whitegrid")
    
    # --- Calculate Mean Power for Each Band, Grouped by State ---
    # This is the core of our analysis. We group all readings by their 'State'
    # and then find the average power for each brainwave band within that state.
    psd_data = df.groupby('State')[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].mean().reset_index()

    # The order of the bands is important for plotting
    band_order = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
    
    # --- Create the Plot ---
    plt.figure(figsize=(12, 7))
    
    # Define colors for each state to make the plot clear
    colors = {'Baseline': 'blue', 'Stressed': 'red', 'Focused': 'green'}
    
    # Plot a line for each state
    for index, row in psd_data.iterrows():
        state = row['State']
        # Get the power values for the bands in the correct order
        power_values = row[band_order].values
        
        plt.plot(band_order, power_values, marker='o', linestyle='-', label=state, color=colors.get(state, 'black'))

    # --- Formatting the Plot ---
    plt.title('Average Power Spectral Density (PSD) by State', fontsize=16)
    plt.xlabel('EEG Frequency Bands', fontsize=12)
    plt.ylabel('Average Power (Magnitude)', fontsize=12)
    plt.legend(title='Mental State')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to load data and generate the PSD plot.
    """
    # --- Load the Data with robust settings---
    try:
        # Using the robust settings from our previous debugging session
        df = pd.read_csv(CSV_FILE, sep=',', engine='python', skipinitialspace=True)
        # Clean column names just in case
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"[ERROR] File not found at: {CSV_FILE}")
        print("Please ensure the CSV file exists and the path is correct.")
        return
    except Exception as e:
        print(f"[ERROR] An error occurred while loading the CSV: {e}")
        return
        
    print("✅ Data loaded successfully. Generating PSD plot...")
    
    plot_psd(df)

if __name__ == "__main__":
    main()