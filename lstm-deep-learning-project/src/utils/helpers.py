def plot_loss(history):
    """
    Plots the training and validation loss over epochs.

    Parameters:
    history (History): The history object returned by the Keras model's fit method.
    """
    import matplotlib.pyplot as plt

    # Extract loss values from the history object
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(loss) + 1)

    # Plot training and validation loss
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid()
    plt.show()


def plot_predictions(y_true, y_pred):
    """
    Plots the true values against the predicted values.

    Parameters:
    y_true (array-like): The true values.
    y_pred (array-like): The predicted values from the model.
    """
    import matplotlib.pyplot as plt

    # Create a figure for the plot
    plt.figure(figsize=(10, 6))
    plt.plot(y_true, label='True Values', color='blue')
    plt.plot(y_pred, label='Predicted Values', color='red')
    plt.title('True vs Predicted Values')
    plt.xlabel('Time Steps')
    plt.ylabel('Values')
    plt.legend()
    plt.grid()
    plt.show()