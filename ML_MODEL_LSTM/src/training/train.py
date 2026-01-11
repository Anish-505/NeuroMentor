def train_model(model, train_data, val_data, epochs, batch_size, model_save_path):
    """
    Train the LSTM model with the provided training and validation data.

    Parameters:
    model: The LSTM model to be trained.
    train_data: Tuple containing training features and labels.
    val_data: Tuple containing validation features and labels.
    epochs: Number of epochs to train the model.
    batch_size: Size of the batches for training.
    model_save_path: Path to save the best model based on validation loss.

    Returns:
    history: Training history containing loss and accuracy metrics.
    """
    from keras.callbacks import ModelCheckpoint
    from keras.optimizers import Adam

    # Unpack training and validation data
    X_train, y_train = train_data
    X_val, y_val = val_data

    # Compile the model with Adam optimizer and mean squared error loss
    model.compile(optimizer=Adam(), loss='mean_squared_error')

    # Define a callback to save the best model
    checkpoint = ModelCheckpoint(model_save_path, monitor='val_loss', save_best_only=True, mode='min')

    # Train the model
    history = model.fit(X_train, y_train, 
                        validation_data=(X_val, y_val), 
                        epochs=epochs, 
                        batch_size=batch_size, 
                        callbacks=[checkpoint])

    return history

if __name__ == "__main__":
    import os
    from src.data.loader import load_data
    from src.data.preprocessing import create_sliding_windows
    from src.models.lstm_model import create_lstm_model

    # Load and preprocess data
    data = load_data('path/to/dataset.csv')
    X, y = create_sliding_windows(data, window_size=10)

    # Split data into training and validation sets
    train_size = int(len(X) * 0.8)
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]

    # Create the LSTM model
    model = create_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))

    # Define training parameters
    epochs = 50
    batch_size = 32
    model_save_path = os.path.join('models', 'best_lstm_model.h5')

    # Train the model
    history = train_model(model, (X_train, y_train), (X_val, y_val), epochs, batch_size, model_save_path)