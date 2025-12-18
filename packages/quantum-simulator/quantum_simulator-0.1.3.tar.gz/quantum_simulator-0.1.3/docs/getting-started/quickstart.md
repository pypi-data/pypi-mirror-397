# Quick Start

This guide will get you up and running with the Quantum Simulator in just a few minutes.

## Your First Quantum Simulation

Let's start with a simple example that creates a single qubit and applies a Hadamard gate:

```python
from quantum_simulator import QuantumSimulator
from quantum_simulator.gates import H_GATE

# Create a 1-qubit simulator
sim = QuantumSimulator(1)
print(f"Initial state: {sim.get_state_vector()}")

# Apply a Hadamard gate to put the qubit in superposition
gate_result = H_GATE.apply(sim.get_state_vector(), [0])
sim.state_vector = gate_result
print(f"After Hadamard: {sim.get_state_vector()}")

# Measure the qubit
result = sim.measure(0)
print(f"Measurement result: {result}")
```

## Creating Bell States

Now let's create a more complex example with two entangled qubits (a Bell state):

```python
from quantum_simulator import QuantumSimulator, QuantumCircuit
from quantum_simulator.gates import H_GATE, CNOT_GATE

# Create a 2-qubit simulator
sim = QuantumSimulator(2)

# Create a circuit to generate a Bell state
circuit = QuantumCircuit(2)
circuit.add_gate(H_GATE, [0])        # Hadamard on qubit 0
circuit.add_gate(CNOT_GATE, [0, 1])  # CNOT: control=0, target=1

print("Circuit:")
print(circuit)

# Execute the circuit
circuit.execute(sim)
print(f"Bell state: {sim.get_state_vector()}")

# Measure both qubits
result0 = sim.measure(0)
result1 = sim.measure(1)
print(f"Measurements: qubit 0 = {result0}, qubit 1 = {result1}")
```

## Understanding the Output

### State Vectors

The state vector represents the quantum state of your system:

- `[1, 0]` for a 1-qubit system means the qubit is in state |0⟩
- `[0, 1]` means the qubit is in state |1⟩  
- `[0.707, 0.707]` means the qubit is in superposition (|0⟩ + |1⟩)/√2

For multi-qubit systems, the state vector grows exponentially:
- 2 qubits: 4 elements representing |00⟩, |01⟩, |10⟩, |11⟩
- 3 qubits: 8 elements, and so on

### Bell State Example

A Bell state `[0.707, 0, 0, 0.707]` represents the entangled state (|00⟩ + |11⟩)/√2, which means:
- 50% probability of measuring both qubits as 0
- 50% probability of measuring both qubits as 1
- 0% probability of measuring different values

## Available Gates

The library includes several common quantum gates:

```python
from quantum_simulator.gates import X_GATE, Y_GATE, Z_GATE, H_GATE, CNOT_GATE

# Single-qubit gates
X_GATE    # Pauli-X (NOT gate)
Y_GATE    # Pauli-Y  
Z_GATE    # Pauli-Z
H_GATE    # Hadamard (creates superposition)

# Two-qubit gates
CNOT_GATE # Controlled-NOT (creates entanglement)
```

## Building Custom Circuits

You can build complex circuits by chaining multiple gates:

```python
from quantum_simulator import QuantumSimulator, QuantumCircuit
from quantum_simulator.gates import H_GATE, X_GATE, Z_GATE

sim = QuantumSimulator(2)
circuit = QuantumCircuit(2)

# Add multiple gates
circuit.add_gate(H_GATE, [0])     # Hadamard on qubit 0
circuit.add_gate(X_GATE, [1])     # X gate on qubit 1  
circuit.add_gate(Z_GATE, [0])     # Z gate on qubit 0

# Execute the entire circuit
circuit.execute(sim)

print(f"Final state: {sim.get_state_vector()}")
```

## Next Steps

Now that you've learned the basics, explore more advanced topics:

- [Examples](examples.md) - More complex quantum algorithms
- [Quantum Simulators](../user-guide/simulators.md) - Deep dive into the simulation engine
- [Quantum Gates](../user-guide/gates.md) - Learn about all available gates
- [Quantum Circuits](../user-guide/circuits.md) - Advanced circuit construction