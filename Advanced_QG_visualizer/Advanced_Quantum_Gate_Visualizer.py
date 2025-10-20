# Advanced Quantum Gate Visualizer / Simulator (6-qubit live Bloch spheres)
import tkinter as tk
from tkinter import messagebox
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

max_qubits = 6
qc = QuantumCircuit(max_qubits)
applied_gates = []
ani = None

# ------------------- Functions -------------------

def reset_circuit():
    global qc, applied_gates
    qc = QuantumCircuit(max_qubits)
    applied_gates = []
    messagebox.showinfo("Reset", "Quantum circuit reset!")

def apply_gate():
    global qc, applied_gates
    try:
        q = int(qubit_var.get())
        if q < 0 or q >= max_qubits:
            messagebox.showerror("Error", f"Select qubit 0-{max_qubits-1}")
            return
    except:
        messagebox.showerror("Error", "Invalid qubit selection!")
        return

    gate = gate_var.get()
    try:
        if gate == "X": qc.x(q)
        elif gate == "Y": qc.y(q)
        elif gate == "Z": qc.z(q)
        elif gate == "H": qc.h(q)
        elif gate == "S": qc.s(q)
        elif gate == "T": qc.t(q)
        elif gate == "RX": qc.rx(float(angle_entry.get()), q)
        elif gate == "RY": qc.ry(float(angle_entry.get()), q)
        elif gate == "RZ": qc.rz(float(angle_entry.get()), q)
        elif gate == "CNOT": qc.cx(q, int(target_qubit_var.get()))
        elif gate == "CZ": qc.cz(q, int(target_qubit_var.get()))
        elif gate == "SWAP": qc.swap(q, int(target_qubit_var.get()))
        elif gate == "CCX": qc.ccx(q, int(target_qubit_var.get()), int(target2_qubit_var.get()))
        else: messagebox.showerror("Error", "Unknown gate!"); return

        applied_gates.append(gate)
        messagebox.showinfo("Applied", f"{gate} applied to qubit(s)!")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input! {e}")

# ------------------- Bloch Vector -------------------
def bloch_vector(state, qubit_index):
    dm = partial_trace(state, [i for i in range(max_qubits) if i != qubit_index])
    x = np.real(np.trace(dm.data @ np.array([[0,1],[1,0]])))
    y = np.real(np.trace(dm.data @ np.array([[0,-1j],[1j,0]])))
    z = np.real(np.trace(dm.data @ np.array([[1,0],[0,-1]])))
    return np.array([x,y,z])

# ------------------- Visualizer -------------------
def visualize():
    global qc, ani
    state = Statevector.from_instruction(qc)

    fig = plt.figure(figsize=(20,5))
    axs = [fig.add_subplot(1,max_qubits,i+1,projection='3d') for i in range(max_qubits)]

    # Sphere coordinates
    u,v = np.mgrid[0:2*np.pi:30j,0:np.pi:15j]
    sphere_x = np.cos(u)*np.sin(v)
    sphere_y = np.sin(u)*np.sin(v)
    sphere_z = np.cos(v)
    arrows = []

    for ax in axs:
        ax.plot_wireframe(sphere_x,sphere_y,sphere_z,color='lightgray',linewidth=0.5)
        ax.set_xlim([-1,1]); ax.set_ylim([-1,1]); ax.set_zlim([-1,1])
        ax.axis('off')
        arrow, = ax.plot([0,0],[0,0],[0,0],color='r',lw=3)
        arrows.append(arrow)

    def update(frame):
        angle = np.radians(frame)
        for i, ax in enumerate(axs):
            vec = bloch_vector(state,i)
            # Rotate around z-axis
            R = np.array([[np.cos(angle), -np.sin(angle),0],
                          [np.sin(angle), np.cos(angle),0],
                          [0,0,1]])
            rotated_vec = R @ vec
            arrows[i].set_data([0,rotated_vec[0]],[0,rotated_vec[1]])
            arrows[i].set_3d_properties([0,rotated_vec[2]])
            ax.view_init(elev=30, azim=frame)
        return arrows

    ani = FuncAnimation(fig, update, frames=360, interval=50, blit=False)
    plt.show()

    # Show circuit diagram
    qc.draw('mpl')
    plt.show()

# ------------------- GUI -------------------
root = tk.Tk()
root.title("Advanced Quantum Gate Visualizer / Simulator")

tk.Label(root, text=f"Select Qubit (0-{max_qubits-1}):").pack()
qubit_var = tk.StringVar()
tk.Entry(root,textvariable=qubit_var).pack()
qubit_var.set("0")

tk.Label(root,text=f"Target Qubit (for 2-qubit gates, 0-{max_qubits-1}):").pack()
target_qubit_var = tk.StringVar()
tk.Entry(root,textvariable=target_qubit_var).pack()
target_qubit_var.set("1")

tk.Label(root,text=f"Second Target Qubit (for CCX, 0-{max_qubits-1}):").pack()
target2_qubit_var = tk.StringVar()
tk.Entry(root,textvariable=target2_qubit_var).pack()
target2_qubit_var.set("2")

tk.Label(root,text="Select Gate:").pack()
gate_var = tk.StringVar()
tk.OptionMenu(root, gate_var,
              "X","Y","Z","H","S","T",
              "RX","RY","RZ",
              "CNOT","CZ","SWAP","CCX").pack()
gate_var.set("X")

tk.Label(root,text="Angle (RX, RY, RZ in radians):").pack()
angle_entry = tk.Entry(root); angle_entry.pack(); angle_entry.insert(0,"3.1415")

tk.Button(root,text="Apply Gate",command=apply_gate).pack(pady=5)
tk.Button(root,text="Reset Circuit",command=reset_circuit).pack(pady=5)
tk.Button(root,text="Visualize Circuit & Bloch Sphere",command=visualize).pack(pady=10)

root.mainloop()