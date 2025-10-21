import tkinter as tk
from tkinter import messagebox
from qiskit import QuantumCircuit
from qiskit.visualization import plot_bloch_vector
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------- Function to get Bloch vector from statevector ----------------
def get_bloch_vector(state):
    alpha = state[0]
    beta = state[1]
    x = 2 * np.real(np.conj(alpha) * beta)
    y = 2 * np.imag(np.conj(alpha) * beta)
    z = np.abs(alpha)**2 - np.abs(beta)**2
    return [x, y, z]

# ---------------- Main Visualization Function ----------------
def apply_gate(gate_name):
    qc = QuantumCircuit(1)
    if gate_name == "H":
        qc.h(0)
    elif gate_name == "X":
        qc.x(0)
    elif gate_name == "Y":
        qc.y(0)
    elif gate_name == "Z":
        qc.z(0)
    elif gate_name == "Reset":
        update_plot([0, 0, 1], "Initial State |0⟩")
        return

    # Updated for Qiskit 1.2+
    state = np.array(qc.data[-1].operation.to_matrix().dot([1, 0]))
    bloch = get_bloch_vector(state)
    update_plot(bloch, f"After {gate_name} Gate")

# ---------------- Update Matplotlib Plot ----------------
def update_plot(bloch_vector, title):
    ax.clear()
    plot_bloch_vector(bloch_vector, ax=ax)

    # Title style
    ax.set_title(title, fontsize=14, color="white", pad=20, loc='center')
    ax.set_facecolor("#101820")

    # Make all Bloch sphere labels white
    for text in ax.texts:
        text.set_color("white")

    # Axis labels white (extra safety)
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.zaxis.label.set_color("white")

    canvas.draw()

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Quantum Superposition Visualizer")
root.geometry("700x600")
root.configure(bg="#101820")

title_label = tk.Label(
    root,
    text="🌀 Quantum Superposition Visualizer 🧠",
    font=("Helvetica", 18, "bold"),
    fg="#FEE715",
    bg="#101820"
)
title_label.pack(pady=10)

# Matplotlib Figure
fig = plt.Figure(figsize=(5, 4), facecolor="#101820")
ax = fig.add_subplot(111, projection='3d')
plot_bloch_vector([0, 0, 1], ax=ax)

# White labels for initial state
for text in ax.texts:
    text.set_color("white")

ax.set_title("Initial State |0⟩", fontsize=14, color="white", pad=20, loc='center')
ax.set_facecolor("#101820")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Buttons
btn_frame = tk.Frame(root, bg="#101820")
btn_frame.pack()

for gate in ["H", "X", "Y", "Z", "Reset"]:
    tk.Button(
        btn_frame,
        text=gate + " Gate" if gate != "Reset" else "Reset",
        font=("Helvetica", 14, "bold"),
        bg="#FEE715" if gate != "Reset" else "#FF4C4C",
        fg="black",
        width=10,
        height=2,
        command=lambda g=gate: apply_gate(g)
    ).grid(row=0, column=["H", "X", "Y", "Z", "Reset"].index(gate), padx=10)

root.mainloop()

