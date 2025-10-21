import tkinter as tk
from tkinter import messagebox
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# ---------------- Quantum Measurement Function ----------------
def measure_entangled_qubits():
    qc = QuantumCircuit(2, 2)   # 2 qubits, 2 classical bits
    qc.h(0)                      # Put qubit 0 in superposition
    qc.cx(0, 1)                  # Entangle qubit 0 with qubit 1
    qc.measure([0, 1], [0, 1])  # Measure both qubits

    simulator = AerSimulator()
    tqc = transpile(qc, simulator)
    result = simulator.run(tqc, shots=1).result()
    counts = result.get_counts()
    outcome = list(counts.keys())[0]  # e.g., '00', '11', etc.
    return outcome

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Quantum Entanglement Game")

score_p1 = 0
score_p2 = 0

score_label = tk.Label(root, text=f"Player 1: {score_p1} | Player 2: {score_p2}", font=("Arial", 14))
score_label.pack(pady=10)

# ---------------- Game Logic ----------------
def play_move():
    global score_p1, score_p2
    outcome = measure_entangled_qubits()
    
    if outcome == '00':
        score_p1 += 1
        score_p2 += 1
        msg = "Both qubits measured 0! Both players get 1 point."
    elif outcome == '11':
        score_p1 += 2
        score_p2 += 2
        msg = "Both qubits measured 1! Both players get 2 points."
    elif outcome == '01':
        score_p1 += 1
        msg = "Player 1 got 0, Player 2 got 1. Player 1 gets 1 point."
    else:  # '10'
        score_p2 += 1
        msg = "Player 1 got 1, Player 2 got 0. Player 2 gets 1 point."

    score_label.config(text=f"Player 1: {score_p1} | Player 2: {score_p2}")
    messagebox.showinfo("Quantum Move Result", f"Outcome: {outcome}\n{msg}")

# ---------------- Play Button ----------------
play_button = tk.Button(root, text="Play Move", font=("Arial", 12), command=play_move)
play_button.pack(pady=20)

root.mainloop()
