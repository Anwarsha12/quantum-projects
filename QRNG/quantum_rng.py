import tkinter as tk
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import random

# Function to generate a quantum random number
def quantum_random_number():
    qc = QuantumCircuit(1, 1)
    qc.h(0)             # Put qubit in superposition
    qc.measure(0, 0)    # Measure qubit (gives 0 or 1 randomly)

    simulator = AerSimulator()
    tqc = transpile(qc, simulator)
    result = simulator.run(tqc, shots=1).result()
    counts = result.get_counts()
    
    bit = list(counts.keys())[0]
    return int(bit)

# Function to generate an N-bit quantum random number
def generate_random():
    bits = int(entry_bits.get())
    number = ""
    for _ in range(bits):
        number += str(quantum_random_number())
    result_label.config(text=f"Quantum Random Number: {number}")

# GUI Setup
root = tk.Tk()
root.title("Quantum Random Number Generator (QRNG)")
root.geometry("400x300")
root.config(bg="#101820")

title_label = tk.Label(root, text="🔮 Quantum RNG", font=("Arial", 20, "bold"), fg="#FEE715", bg="#101820")
title_label.pack(pady=10)

entry_label = tk.Label(root, text="Enter number of bits:", fg="white", bg="#101820")
entry_label.pack(pady=5)

entry_bits = tk.Entry(root, justify="center", width=10)
entry_bits.insert(0, "8")
entry_bits.pack()

generate_button = tk.Button(root, text="Generate", command=generate_random, bg="#FEE715", fg="#101820", font=("Arial", 12, "bold"))
generate_button.pack(pady=15)

result_label = tk.Label(root, text="Quantum Random Number: ", fg="white", bg="#101820", font=("Arial", 12))
result_label.pack(pady=20)

root.mainloop()
