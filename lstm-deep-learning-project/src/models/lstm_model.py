def create_lstm_model(input_shape, num_classes, dropout_rate=0.2, learning_rate=0.001):
    """
    Create and compile an LSTM model.

    Parameters:
    - input_shape: Tuple representing the shape of the input data (timesteps, features).
    - num_classes: Integer representing the number of output classes.
    - dropout_rate: Float representing the dropout rate for regularization.
    - learning_rate: Float representing the learning rate for the optimizer.

    Returns:
    - model: Compiled Keras LSTM model.
    """
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam

    # Initialize the model
    model = Sequential()

    # Add LSTM layer
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(dropout_rate))

    # Add another LSTM layer
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(dropout_rate))

    # Add the output layer
    model.add(Dense(num_classes, activation='softmax'))

    # Compile the model
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='categorical_crossentropy', metrics=['accuracy'])

    return model