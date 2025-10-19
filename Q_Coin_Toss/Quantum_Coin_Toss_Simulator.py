import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
try:
    from qiskit_aer import AerSimulator
    AER_AVAILABLE = True
except ImportError:
    AER_AVAILABLE = False

# -------------------- Quantum Coin Toss --------------------
def quantum_coin_toss(shots):
    if not AER_AVAILABLE:
        messagebox.showerror("Error", "AerSimulator not available. Install qiskit-aer.")
        return None
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # Apply Hadamard to create superposition
    qc.measure(0, 0)
    
    sim = AerSimulator()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()
    return counts

def toss():
    try:
        shots = int(shots_entry.get())
        if shots <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a positive integer for shots.")
        return
    
    counts = quantum_coin_toss(shots)
    if counts:
        plt.bar(counts.keys(), counts.values(), color=['blue', 'red'])
        plt.title(f"Quantum Coin Toss Results ({shots} shots)")
        plt.xlabel("Outcome")
        plt.ylabel("Counts")
        plt.show()

# -------------------- GUI --------------------
root = tk.Tk()
root.title("Quantum Coin Toss Simulator")
root.geometry("300x150")
root.configure(bg="#101820")

title_label = tk.Label(root, text="Quantum Coin Toss Simulator", fg="white", bg="#101820", font=("Arial", 14))
title_label.pack(pady=10)

shots_frame = tk.Frame(root, bg="#101820")
shots_frame.pack(pady=5)

shots_label = tk.Label(shots_frame, text="Number of tosses:", fg="white", bg="#101820")
shots_label.pack(side="left", padx=5)

shots_entry = tk.Entry(shots_frame, justify="center", width=10)
shots_entry.insert(0, "10")
shots_entry.pack(side="left")

toss_button = tk.Button(root, text="Toss Coin", command=toss, width=15)
toss_button.pack(pady=10)

root.mainloop()
