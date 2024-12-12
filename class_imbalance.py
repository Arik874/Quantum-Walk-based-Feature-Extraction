from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split

def compute_class_weights(labels):
    """
    Compute class weights for imbalanced datasets.
    """
    unique_classes = np.unique(labels)
    class_weights = compute_class_weight(class_weight='balanced', classes=unique_classes, y=labels)
    return dict(zip(unique_classes, class_weights))

def weighted_initialization(data, class_weights):
    """
    Apply weighted initialization based on class weights.
    """
    weighted_data = np.copy(data)
    for i, value in enumerate(data):
        if value > 0:
            weighted_data[i] *= class_weights.get(1, 1)  # Adjust weights for positive samples
        else:
            weighted_data[i] *= class_weights.get(0, 1)  # Adjust weights for negative samples
    return weighted_data

@qml.qnode(dev)
def hybrid_quantum_walk_with_weights(data, steps=3, class_weights=None):
    """
    Implements a hybrid quantum walk with weighted initialization.
    """
    # Apply weighted initialization to the input data
    if class_weights is not None:
        data = weighted_initialization(data, class_weights)

    # Initialize quantum state
    for i in range(num_position_qubits):
        if data[i] > 0:
            qml.Hadamard(wires=i)
        else:
            qml.PauliX(wires=i)
    
    # Encode coin qubit for signal properties
    qml.RY(np.pi * data[-1], wires=num_position_qubits)

    # Quantum walk steps
    for _ in range(steps):
        qml.Hadamard(wires=num_position_qubits)  # Coin operator
        for control in range(num_position_qubits - 1):
            qml.CNOT(wires=[control, control + 1])  # Shift operator
    
    # Measurement
    return [qml.expval(qml.PauliZ(i)) for i in range(num_qubits)]

# Example labels for class imbalance handling
labels = np.array([0, 1, 1, 2, 0, 1, 2, 2, 0, 1])  # Example class labels for testing
class_weights = compute_class_weights(labels)
print("Computed Class Weights:", class_weights)

# Example data
data = np.array([1, 0, 1, 0.5])  # Binary and continuous data
weighted_features = hybrid_quantum_walk_with_weights(data, steps=3, class_weights=class_weights)
print("Features with Class Weights:", weighted_features)

# Splitting data
X_train, X_val, y_train, y_val = train_test_split(
    np.array([weighted_features]), labels, test_size=0.3, random_state=42, stratify=labels
)
