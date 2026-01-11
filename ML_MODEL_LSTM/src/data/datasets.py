class TimeSeriesDataset:
    def __init__(self, data, sequence_length, train_size=0.8):
        """
        Initializes the TimeSeriesDataset with the provided data and parameters.

        Parameters:
        data (array-like): The input time series data.
        sequence_length (int): The length of the sequences to create.
        train_size (float): The proportion of the dataset to include in the train split.
        """
        self.data = data
        self.sequence_length = sequence_length
        self.train_size = train_size
        self.train_data, self.test_data = self.split_data()

    def split_data(self):
        """
        Splits the data into training and testing sets based on the specified train size.

        Returns:
        tuple: A tuple containing the training and testing datasets.
        """
        train_size = int(len(self.data) * self.train_size)
        train_data = self.data[:train_size]
        test_data = self.data[train_size:]
        return train_data, test_data

    def create_sequences(self):
        """
        Creates sequences from the dataset for LSTM input.

        Returns:
        tuple: A tuple containing the input sequences and their corresponding targets.
        """
        sequences = []
        targets = []
        for i in range(len(self.train_data) - self.sequence_length):
            seq = self.train_data[i:i + self.sequence_length]
            target = self.train_data[i + self.sequence_length]
            sequences.append(seq)
            targets.append(target)
        return np.array(sequences), np.array(targets)

    def get_train_data(self):
        """
        Returns the training data sequences and targets.

        Returns:
        tuple: A tuple containing the training sequences and targets.
        """
        return self.create_sequences()

    def get_test_data(self):
        """
        Returns the testing data sequences and targets.

        Returns:
        tuple: A tuple containing the testing sequences and targets.
        """
        sequences = []
        targets = []
        for i in range(len(self.test_data) - self.sequence_length):
            seq = self.test_data[i:i + self.sequence_length]
            target = self.test_data[i + self.sequence_length]
            sequences.append(seq)
            targets.append(target)
        return np.array(sequences), np.array(targets)