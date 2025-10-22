# Quantum Roulette Simulator
import tkinter as tk
from tkinter import messagebox
from qiskit import QuantumCircuit, transpile
try:
    from qiskit_aer import AerSimulator
    AER_AVAILABLE = True
except ImportError:
    AER_AVAILABLE = False

# ------------------- Quantum Roulette Function -------------------
def quantum_roulette():
    if not AER_AVAILABLE:
        messagebox.showerror("Error", "qiskit-aer is not installed!")
        return
    
    try:
        n_qubits = 6  # Enough for 0-36 roulette numbers
        qc = QuantumCircuit(n_qubits, n_qubits)

        # Put all qubits in superposition
        for q in range(n_qubits):
            qc.h(q)

        # Measure qubits
        qc.measure(range(n_qubits), range(n_qubits))

        # Simulate
        simulator = AerSimulator()
        t_qc = transpile(qc, simulator)
        result = simulator.run(t_qc, shots=1).result()  # Direct run, no assemble needed
        counts = result.get_counts()

        # Convert binary outcome to decimal
        outcome_bin = list(counts.keys())[0]
        outcome_dec = int(outcome_bin, 2)
        if outcome_dec > 36:
            outcome_dec = outcome_dec % 37

        # Show result
        messagebox.showinfo("Quantum Roulette", f"The ball landed on: {outcome_dec}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ------------------- GUI -------------------
root = tk.Tk()
root.title("Quantum Roulette Simulator")
root.geometry("400x200")
root.configure(bg="#1e1e1e")

# Heading
heading = tk.Label(root, text="🎲 Quantum Roulette Simulator 🎲", font=("Helvetica", 16, "bold"), bg="#1e1e1e", fg="white")
heading.pack(pady=20)

# Spin button
spin_button = tk.Button(root, text="Spin the Wheel", font=("Helvetica", 14), bg="#4caf50", fg="white", command=quantum_roulette)
spin_button.pack(pady=20)

root.mainloop()
