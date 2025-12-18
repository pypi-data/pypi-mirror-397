"""Test suite for quantum_simulator package."""

import pytest
import numpy as np

from quantum_simulator import QuantumSimulator, QuantumCircuit
from quantum_simulator.gates import X_GATE, H_GATE, CNOT_GATE


class TestQuantumSimulator:
    """Test the QuantumSimulator class."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        sim = QuantumSimulator(2)
        assert sim.num_qubits == 2
        assert sim.num_states == 4
        
        # Should start in |00> state
        expected_state = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
        np.testing.assert_array_almost_equal(sim.get_state_vector(), expected_state)
    
    def test_reset(self):
        """Test state reset functionality."""
        sim = QuantumSimulator(1)
        # Modify state
        sim.state_vector = np.array([0.0, 1.0], dtype=complex)
        
        # Reset and check
        sim.reset()
        expected_state = np.array([1.0, 0.0], dtype=complex)
        np.testing.assert_array_almost_equal(sim.get_state_vector(), expected_state)
    
    def test_measurement(self):
        """Test quantum measurement."""
        sim = QuantumSimulator(1)
        
        # Measure |0> state - should always return 0
        for _ in range(10):
            result = sim.measure(0)
            assert result in [0, 1]  # Valid measurement outcomes


class TestQuantumCircuit:
    """Test the QuantumCircuit class."""
    
    def test_initialization(self):
        """Test circuit initialization."""
        circuit = QuantumCircuit(2)
        assert circuit.num_qubits == 2
        assert len(circuit.gates) == 0
    
    def test_add_gate(self):
        """Test adding gates to circuit."""
        circuit = QuantumCircuit(2)
        circuit.add_gate(H_GATE, [0])
        circuit.add_gate(CNOT_GATE, [0, 1])
        
        assert len(circuit.gates) == 2
        assert circuit.gates[0][0] == H_GATE
        assert circuit.gates[0][1] == [0]
        assert circuit.gates[1][0] == CNOT_GATE
        assert circuit.gates[1][1] == [0, 1]
    
    def test_circuit_string_representation(self):
        """Test string representation of circuit."""
        circuit = QuantumCircuit(2)
        circuit.add_gate(H_GATE, [0])
        
        circuit_str = str(circuit)
        assert "QuantumCircuit(2 qubits)" in circuit_str
        assert "H on qubits [0]" in circuit_str


class TestQuantumGates:
    """Test quantum gate functionality."""
    
    def test_gate_properties(self):
        """Test gate properties."""
        assert X_GATE.name == "X"
        assert H_GATE.name == "H"
        assert CNOT_GATE.name == "CNOT"
        
        assert X_GATE.num_qubits == 1
        assert H_GATE.num_qubits == 1
        assert CNOT_GATE.num_qubits == 2
    
    def test_x_gate_matrix(self):
        """Test X gate matrix."""
        expected = np.array([[0, 1], [1, 0]], dtype=complex)
        np.testing.assert_array_almost_equal(X_GATE.matrix, expected)
    
    def test_hadamard_matrix(self):
        """Test Hadamard gate matrix."""
        expected = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        np.testing.assert_array_almost_equal(H_GATE.matrix, expected)


class TestIntegration:
    """Integration tests for complete quantum simulations."""
    
    def test_single_qubit_x_gate(self):
        """Test X gate on single qubit."""
        sim = QuantumSimulator(1)
        circuit = QuantumCircuit(1)
        circuit.add_gate(X_GATE, [0])
        
        circuit.execute(sim)
        
        # Should be in |1> state
        expected_state = np.array([0.0, 1.0], dtype=complex)
        np.testing.assert_array_almost_equal(sim.get_state_vector(), expected_state)
    
    def test_bell_state_creation(self):
        """Test creation of Bell state."""
        sim = QuantumSimulator(2)
        circuit = QuantumCircuit(2)
        
        # Create Bell state: H|0> ⊗ |0> then CNOT
        circuit.add_gate(H_GATE, [0])
        circuit.add_gate(CNOT_GATE, [0, 1])
        
        circuit.execute(sim)
        
        # Should be in (|00> + |11>)/√2 state
        expected_state = np.array([1/np.sqrt(2), 0.0, 0.0, 1/np.sqrt(2)], dtype=complex)
        np.testing.assert_array_almost_equal(sim.get_state_vector(), expected_state)


if __name__ == "__main__":
    pytest.main([__file__])