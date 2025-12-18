# Quantum Simulator

Welcome to the **Quantum Simulator** documentation! This library provides a Python interface for simulating quantum computers and quantum algorithms.

## Features

- 🔬 **Quantum State Simulation**: Accurate simulation of quantum states using state vectors
- 🚪 **Quantum Gates**: Implementation of common single and multi-qubit gates
- 🔗 **Quantum Circuits**: Build and execute complex quantum circuits
- 📊 **Measurement**: Simulate quantum measurements with proper state collapse
- 🎯 **Easy to Use**: Clean, intuitive API for quantum programming

## Quick Example

```python
from quantum_simulator import QuantumSimulator, QuantumCircuit
from quantum_simulator.gates import H_GATE, CNOT_GATE

# Create a 2-qubit quantum simulator
sim = QuantumSimulator(2)

# Build a Bell state circuit
circuit = QuantumCircuit(2)
circuit.add_gate(H_GATE, [0])      # Hadamard on qubit 0
circuit.add_gate(CNOT_GATE, [0, 1])  # CNOT with control=0, target=1

# Execute the circuit
circuit.execute(sim)

# Measure the qubits
result0 = sim.measure(0)
result1 = sim.measure(1)
print(f"Measurement: {result0}, {result1}")
```

## Getting Started

- [Installation Guide](getting-started/installation.md) - How to install the package
- [Quick Start](getting-started/quickstart.md) - Your first quantum simulation
- [Examples](getting-started/examples.md) - More complex examples and use cases

## User Guide

- [Quantum Simulators](user-guide/simulators.md) - Understanding the simulation engine
- [Quantum Gates](user-guide/gates.md) - Available gates and how to use them
- [Quantum Circuits](user-guide/circuits.md) - Building and executing quantum circuits

## API Reference

Complete API documentation is available in the [API Reference](reference/) section.

## Development

Want to contribute? Check out our [Contributing Guide](development/contributing.md) and [Publishing Guide](development/publishing.md).

## License

This project is licensed under the Unlicense - see the [LICENSE](https://github.com/beefy/quantum-simulator/blob/main/LICENSE) file for details.