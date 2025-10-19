import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

# ----------------- Quantum Teleportation Function -----------------
def quantum_teleportation(state_choice):
    # 3-qubit circuit: q0=state, q1=entanglement, q2=target
    qc = QuantumCircuit(3, 3)

    # Prepare the state to teleport
    if state_choice == "|0>":
        pass  # Already |0>
    elif state_choice == "|1>":
        qc.x(0)
    elif state_choice == "|+>":
        qc.h(0)
    elif state_choice == "|->":
        qc.x(0)
        qc.h(0)

    # Step 1: Create entanglement between qubit 1 and 2
    qc.h(1)
    qc.cx(1, 2)

    # Step 2: Bell measurement on qubit 0 and 1
    qc.cx(0, 1)
    qc.h(0)

    # Step 3: Measure qubits 0 and 1
    qc.measure([0, 1], [0, 1])

    # Step 4: Conditional operations on qubit 2
    qc.cx(1, 2)
    qc.cz(0, 2)

    # Step 5: Measure the teleported qubit
    qc.measure(2, 2)

    return qc

# ----------------- Run Simulation -----------------
def run_teleportation():
    state = state_var.get()
    qc = quantum_teleportation(state)

    # Run on simulator
    sim = AerSimulator()
    tqc = transpile(qc, sim)
    result = sim.run(tqc).result()  # No assemble() needed
    counts = result.get_counts()

    messagebox.showinfo("Results", f"Measurement Results: {counts}")
    plot_histogram(counts)
    plt.show()

# ----------------- GUI Setup -----------------
root = tk.Tk()
root.title("Quantum Teleportation Simulator")
root.geometry("450x200")
root.config(bg="#101820")

title_label = tk.Label(root, text="Quantum Teleportation (3-Qubit)", fg="white", bg="#101820", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

state_var = tk.StringVar(value="|+>")
state_frame = tk.Frame(root, bg="#101820")
state_frame.pack(pady=10)

tk.Label(state_frame, text="Select State to Teleport:", fg="white", bg="#101820").pack(side="left", padx=5)
state_options = ["|0>", "|1>", "|+>", "|->"]
state_menu = tk.OptionMenu(state_frame, state_var, *state_options)
state_menu.pack(side="left")

run_button = tk.Button(root, text="Run Teleportation", command=run_teleportation, bg="#f0c674", fg="black", width=20)
run_button.pack(pady=20)

root.mainloop()
