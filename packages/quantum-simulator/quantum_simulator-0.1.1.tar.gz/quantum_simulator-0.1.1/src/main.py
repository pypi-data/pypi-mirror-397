
"""
Example usage of the quantum simulator.
"""

from quantum_simulator import QuantumSimulator, QuantumCircuit, QuantumGate
from quantum_simulator.gates import H_GATE, X_GATE, CNOT_GATE


def main() -> None:
    """Example quantum simulation."""
    print("Quantum Simulator Example")
    print("=" * 30)
    
    # Create a 2-qubit simulator
    sim = QuantumSimulator(2)
    print(f"Initial state: {sim.get_state_vector()}")
    
    # Create a simple circuit
    circuit = QuantumCircuit(2)
    circuit.add_gate(H_GATE, [0])  # Hadamard gate on qubit 0
    circuit.add_gate(CNOT_GATE, [0, 1])  # CNOT gate with control=0, target=1
    
    print(f"\nCircuit:\n{circuit}")
    
    # Execute the circuit
    circuit.execute(sim)
    print(f"Final state: {sim.get_state_vector()}")
    
    # Measure both qubits
    result0 = sim.measure(0)
    result1 = sim.measure(1)
    print(f"Measurement results: qubit 0 = {result0}, qubit 1 = {result1}")


if __name__ == "__main__":
    main()
