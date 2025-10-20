# Quantum Gate Visualizer Tool

import tkinter as tk
from tkinter import messagebox
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# ------------------- Function to apply gate -------------------
def apply_gate():
    gate = gate_var.get()  # Get selected gate
    try:
        # Get number of qubits from user input
        num_qubits = int(qubits_entry.get())
        if num_qubits < 1 or num_qubits > 2:
            messagebox.showerror("Error", "Number of qubits must be 1 or 2.")
            return
    except:
        messagebox.showerror("Error", "Invalid number of qubits!")
        return

    qc = QuantumCircuit(num_qubits)

    # Apply selected gate
    if gate == "X":
        qc.x(0)  # Apply X gate to first qubit
    elif gate == "H":
        qc.h(0)  # Apply H gate to first qubit
    elif gate == "CNOT":
        if num_qubits < 2:
            messagebox.showerror("Error", "CNOT needs 2 qubits!")
            return
        qc.cx(0, 1)  # Apply CNOT: control=0, target=1
    else:
        messagebox.showerror("Error", "Please select a gate!")
        return

    # Simulate state
    state = Statevector.from_instruction(qc)

    # Plot Bloch vectors for visualization
    fig = plot_bloch_multivector(state)
    plt.show()

# ------------------- GUI Setup -------------------
root = tk.Tk()
root.title("Quantum Gate Visualizer Tool")

# Number of qubits
tk.Label(root, text="Number of Qubits (1 or 2):").pack()
qubits_entry = tk.Entry(root)
qubits_entry.pack()
qubits_entry.insert(0, "1")  # Default 1 qubit

# Gate selection
tk.Label(root, text="Select Gate:").pack()
gate_var = tk.StringVar()
tk.Radiobutton(root, text="X", variable=gate_var, value="X").pack()
tk.Radiobutton(root, text="H", variable=gate_var, value="H").pack()
tk.Radiobutton(root, text="CNOT", variable=gate_var, value="CNOT").pack()

# Apply button
apply_btn = tk.Button(root, text="Apply Gate & Visualize", command=apply_gate)
apply_btn.pack(pady=10)

root.mainloop()
