import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
try:
    from qiskit_aer import AerSimulator
    AER_AVAILABLE = True
except ImportError:
    AER_AVAILABLE = False
from qiskit.visualization import plot_histogram

# ----------------- Quantum Entanglement / Bell State Function -----------------
def create_bell_state(state_type):
    """
    Creates a 2-qubit Bell state circuit based on user selection.
    """
    qc = QuantumCircuit(2, 2)
    
    if state_type == "Φ+ (00 + 11)":
        qc.h(0)
        qc.cx(0, 1)
    elif state_type == "Φ− (00 − 11)":
        qc.h(0)
        qc.cx(0, 1)
        qc.z(0)
    elif state_type == "Ψ+ (01 + 10)":
        qc.h(0)
        qc.cx(0, 1)
        qc.x(0)
    elif state_type == "Ψ− (01 − 10)":
        qc.h(0)
        qc.cx(0, 1)
        qc.x(0)
        qc.z(0)
    else:
        messagebox.showerror("Error", "Invalid Bell state selected!")
        return None
    
    qc.measure([0, 1], [0, 1])
    return qc

# ----------------- Run Simulation -----------------
def run_bell_state():
    if not AER_AVAILABLE:
        messagebox.showerror("Error", "AerSimulator not installed!")
        return
    
    state_choice = bell_var.get()
    qc = create_bell_state(state_choice)
    if qc is None:
        return
    
    sim = AerSimulator()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=1024).result()
    counts = result.get_counts()
    
    messagebox.showinfo("Measurement Result", f"Counts: {counts}")
    
    # Plot histogram
    plt.figure(figsize=(5, 4))
    plot_histogram(counts)
    plt.title(f"Bell State: {state_choice}")
    plt.show()

# ----------------- GUI Setup -----------------
root = tk.Tk()
root.title("Quantum Bell State / Entanglement Demo")
root.geometry("400x250")
root.config(bg="#1e1e2f")

title_label = tk.Label(root, text="Bell State / Entanglement Demo", fg="white", bg="#1e1e2f", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

bell_var = tk.StringVar(value="Φ+ (00 + 11)")
options = ["Φ+ (00 + 11)", "Φ− (00 − 11)", "Ψ+ (01 + 10)", "Ψ− (01 − 10)"]

option_menu = tk.OptionMenu(root, bell_var, *options)
option_menu.config(width=20, font=("Arial", 12))
option_menu.pack(pady=20)

run_button = tk.Button(root, text="Run Bell State", command=run_bell_state, bg="#4caf50", fg="white", font=("Arial", 12))
run_button.pack(pady=10)

note_label = tk.Label(root, text="Requires qiskit-aer installed", fg="lightgray", bg="#1e1e2f", font=("Arial", 10))
note_label.pack(pady=10)

root.mainloop()
