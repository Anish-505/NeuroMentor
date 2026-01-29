/// Technical articles for the focused reading phase
/// Used as fallback when Wikipedia API is unavailable

class Article {
  final String title;
  final String content;
  
  const Article({required this.title, required this.content});
}

const List<Article> localArticles = [
  Article(
    title: 'Neural Network',
    content: '''A neural network is a computational model inspired by the human brain. It consists of layers of interconnected nodes called neurons. Each neuron applies a weighted sum and a non-linear activation function. Neural networks are widely used for classification, regression, image recognition, and many other machine learning tasks.

The basic building block is the perceptron, which takes multiple inputs, applies weights to each, sums them up, adds a bias term, and passes the result through an activation function. Common activation functions include ReLU (Rectified Linear Unit), sigmoid, and tanh.

Deep neural networks contain multiple hidden layers between the input and output layers. This depth allows them to learn hierarchical representations of data. For example, in image recognition, early layers might detect edges, middle layers detect shapes, and deeper layers detect complex objects.

Training a neural network involves adjusting the weights to minimize a loss function. This is typically done using backpropagation and gradient descent. The network makes a prediction, computes the error, and propagates this error backward through the network to update the weights.

Modern advances include convolutional neural networks (CNNs) for images, recurrent neural networks (RNNs) for sequences, and transformers for natural language processing. These architectures have achieved superhuman performance on many tasks.''',
  ),
  
  Article(
    title: 'Microcontroller',
    content: '''A microcontroller is a small computer on a single integrated circuit. It typically includes a processor core, memory, and programmable input-output peripherals. Microcontrollers are used in embedded systems for tasks such as sensor reading, motor control, and communication with other devices.

Unlike general-purpose computers, microcontrollers are designed for specific control applications. They contain both program memory (usually flash) and data memory (RAM) on the same chip. This makes them compact, energy-efficient, and cost-effective for dedicated tasks.

The ESP32, commonly used in IoT projects, is a powerful microcontroller with built-in WiFi and Bluetooth. It features a dual-core processor, multiple GPIO pins, ADC and DAC converters, and support for various communication protocols like I2C, SPI, and UART.

Programming microcontrollers typically involves writing code in C or C++, compiling it for the specific architecture, and flashing it to the device. Many platforms like Arduino provide simplified APIs that make microcontroller programming accessible to beginners.

Common applications include home automation, medical devices, automotive systems, industrial control, and wearable technology. The rise of the Internet of Things has dramatically increased demand for microcontroller-based solutions.''',
  ),
  
  Article(
    title: 'Electroencephalography',
    content: '''Electroencephalography, or EEG, is a non-invasive method for measuring the electrical activity of the brain using electrodes placed on the scalp. Each electrode records tiny voltage changes that arise when large groups of neurons become active together, especially pyramidal cells in the cortex.

A single neuron produces a signal that is far too small to measure at the scalp, but when thousands of neurons fire in synchrony, their electrical fields add up and create a measurable signal that spreads through brain tissue, skull, and skin.

EEG does not capture individual spikes the way an implanted microelectrode might, but instead reflects the summed postsynaptic potentials under each electrode. Because these potentials evolve very quickly, EEG can follow brain dynamics on the order of milliseconds, making it useful for studying fast cognitive processes.

The EEG signal is typically decomposed into frequency bands: Delta (0.5-4 Hz) associated with deep sleep, Theta (4-8 Hz) with drowsiness and light sleep, Alpha (8-13 Hz) with relaxed wakefulness, Beta (13-30 Hz) with active thinking and focus, and Gamma (30+ Hz) with higher cognitive functions.

Brain-computer interfaces use EEG to translate brain activity into commands for external devices. Applications range from helping paralyzed patients communicate to enhancing meditation practice and improving attention in educational settings.''',
  ),
  
  Article(
    title: 'Quantum Computing',
    content: '''Quantum computing is a model of computation that uses quantum-mechanical phenomena such as superposition and entanglement to process information. Instead of classical bits that are strictly 0 or 1, a quantum computer uses qubits that can exist in a combination of states.

Superposition allows a qubit to be in multiple states simultaneously. When you have multiple qubits, the number of possible states grows exponentially. Two qubits can represent four states at once, ten qubits can represent 1024 states, and so on.

Entanglement is a quantum phenomenon where qubits become correlated in such a way that the state of one instantly affects the state of another, regardless of distance. This property enables quantum algorithms to process vast amounts of information in parallel.

By manipulating many qubits together, quantum algorithms can solve certain problems much more efficiently than known classical algorithms. Shor's algorithm can factor large numbers exponentially faster, threatening current encryption. Grover's algorithm provides quadratic speedup for unstructured search.

Current quantum computers are still limited by decoherence and error rates. They require extremely cold temperatures (near absolute zero) to maintain quantum states. Researchers are working on error correction and building more stable qubits to achieve practical quantum advantage.''',
  ),
  
  Article(
    title: 'Machine Learning',
    content: '''Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Instead of following fixed rules, ML algorithms identify patterns in data and use them to make predictions or decisions.

Supervised learning trains models on labeled data, where each input has a known correct output. The model learns to map inputs to outputs and can then generalize to new, unseen data. Common algorithms include linear regression, decision trees, and neural networks.

Unsupervised learning finds patterns in unlabeled data. Clustering algorithms group similar data points together, while dimensionality reduction techniques compress data into fewer features while preserving important information. These methods are useful for exploratory analysis and data preprocessing.

Reinforcement learning trains agents to make decisions by rewarding desired behaviors and punishing undesired ones. The agent interacts with an environment, receives feedback, and learns optimal strategies through trial and error. This approach has achieved remarkable results in game playing and robotics.

Key challenges in machine learning include overfitting (memorizing training data instead of generalizing), bias in training data, interpretability of complex models, and the need for large amounts of labeled data. Active research addresses these issues through techniques like regularization, data augmentation, and explainable AI.''',
  ),
];

/// Get a random article from the local collection
Article getRandomArticle() {
  final index = DateTime.now().millisecondsSinceEpoch % localArticles.length;
  return localArticles[index];
}
