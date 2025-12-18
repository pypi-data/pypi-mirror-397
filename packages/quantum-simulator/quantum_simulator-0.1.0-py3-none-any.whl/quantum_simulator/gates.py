"""
Quantum gates implementation.
"""

import numpy as np
from typing import List


class QuantumGate:
    """Base class for quantum gates."""
    
    def __init__(self, name: str, matrix: np.ndarray):
        """
        Initialize a quantum gate.
        
        Args:
            name: Name of the gate
            matrix: Unitary matrix representing the gate
        """
        self.name = name
        self.matrix = matrix
        self.num_qubits = int(np.log2(matrix.shape[0]))
    
    def apply(self, state_vector: np.ndarray, target_qubits: List[int]) -> np.ndarray:
        """
        Apply the gate to specific qubits.
        
        Args:
            state_vector: Current quantum state vector
            target_qubits: List of qubit indices to apply the gate to
            
        Returns:
            New state vector after applying the gate
        """
        # This is a simplified implementation
        # In a real implementation, you'd need to handle multi-qubit gates properly
        return self.matrix @ state_vector


# Common single-qubit gates
X_GATE = QuantumGate("X", np.array([[0, 1], [1, 0]], dtype=complex))
Y_GATE = QuantumGate("Y", np.array([[0, -1j], [1j, 0]], dtype=complex))
Z_GATE = QuantumGate("Z", np.array([[1, 0], [0, -1]], dtype=complex))
H_GATE = QuantumGate("H", np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2))

# Two-qubit gates
CNOT_GATE = QuantumGate("CNOT", np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0]
], dtype=complex))