"""
Quantum Dice / Multi-Qubit Random Number Game
File: quantum_dice_gui.py

What it does
- Simulates fair dice rolls (1-6) using measurements of 3 qubits (range 0-7) and rejection sampling.
- Provides a clean Tkinter GUI to:
  * Roll a single quantum die (uses Qiskit's AerSimulator if available, otherwise falls back to Python's secrets module).
  * Roll many dice (N shots) and show a histogram of outcomes (1-6).
  * Toggle between 'Quantum (AerSimulator)' and 'Local (secrets)' modes.
  * Adjust number of shots for batch runs.

Why rejection sampling?
- 3 qubits produce 8 equally likely outcomes (0..7). We only need values 1..6 (6 values).
- When we map 0..7 -> 1..6 we must avoid bias. We accept outcomes 0..5 and map +1 -> 1..6; outcomes 6 or 7 are rejected and we re-roll.
- This guarantees a uniform distribution over 1..6.

Dependencies
- Python 3.8+
- tkinter (usually included with CPython)
- matplotlib (for histogram)
- qiskit (optional; if not installed the GUI will still work using secure Python RNG)

Usage
1. Install dependencies (optional qiskit):
   pip install matplotlib qiskit

2. Run:
   python quantum_dice_gui.py

Notes
- If qiskit and qiskit_aer are installed, the app will try to use AerSimulator. If Aer is not present, it will still fall back.
- For demonstrative/educational purposes the script runs a small circuit per roll. For large batches it composes a multi-shot circuit for efficiency.

"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math
import sys
import time
from collections import Counter

# Try to import qiskit Aer simulator; if unavailable, we'll fall back to Python's secrets
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    AER_AVAILABLE = True
except Exception:
    AER_AVAILABLE = False

# Use secrets for secure randomness fallback
import secrets

# matplotlib for histogram
import matplotlib.pyplot as plt

# ------------------ Quantum helpers ------------------

def build_equal_superposition_circuit(n_qubits):
    """Builds an n-qubit circuit that places each qubit into H state (equal superposition)
    and measures them.
    Returns (QuantumCircuit) with measurement added.
    """
    qc = QuantumCircuit(n_qubits, n_qubits)
    for q in range(n_qubits):
        qc.h(q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def bits_to_int(bitstring):
    """Converts a bitstring (like '010') with LSB on the right as Qiskit returns to int.
    We assume bitstring is in MSB..LSB ordering from Qiskit counts keys, so int(bitstring, 2) works.
    """
    return int(bitstring, 2)


def quantum_samples_shots(n_qubits, shots, use_aer=True):
    """Return a list of measurement integers (0..2^n_qubits-1) using quantum simulator if available.
    If AerSimulator not available or use_aer False, returns an empty list (caller should handle fallback).
    """
    if not AER_AVAILABLE or not use_aer:
        return []
    sim = AerSimulator()
    qc = build_equal_superposition_circuit(n_qubits)
    try:
        tqc = transpile(qc, sim)
        job = sim.run(tqc, shots=shots)
        result = job.result()
        counts = result.get_counts()
        # Expand counts into list of integers
        samples = []
        for bitstr, c in counts.items():
            val = bits_to_int(bitstr)
            samples.extend([val] * c)
        return samples
    except Exception as e:
        # Something went wrong with Aer -- return empty list to signal fallback
        print("Aer simulator run failed:", e)
        return []


def quantum_roll_one_rejection(n_qubits=3, use_aer=True):
    """Roll a single fair dice value 1..6 using rejection sampling.
    If use_aer True and Aer available, uses a 1-shot quantum circuit; otherwise uses secrets.randbelow.
    """
    max_val = 2 ** n_qubits
    while True:
        if AER_AVAILABLE and use_aer:
            samples = quantum_samples_shots(n_qubits, shots=1, use_aer=True)
            if not samples:
                # fallback
                bitval = secrets.randbelow(max_val)
            else:
                bitval = samples[0]
        else:
            bitval = secrets.randbelow(max_val)
        if bitval < 6:
            return bitval + 1
        # else reject and repeat


def batch_rolls(n_rolls, n_qubits=3, use_aer=True):
    """Roll n_rolls dice (1..6) and return a list of results.
    For performance, when Aer is available we request all shots at once and then use rejection sampling on the returned integers.
    """
    results = []
    max_val = 2 ** n_qubits
    if AER_AVAILABLE and use_aer:
        # We'll request more shots than needed because some will be rejected.
        # Use an overshoot factor to reduce repeated simulator calls.
        remaining = n_rolls
        overshoot_factor = 1.5
        while remaining > 0:
            shots = max(remaining * 2, int(remaining * overshoot_factor))
            samples = quantum_samples_shots(n_qubits, shots=shots, use_aer=True)
            if not samples:
                # fall back to software if simulator fails
                break
            for val in samples:
                if val < 6:
                    results.append(val + 1)
                    if len(results) >= n_rolls:
                        break
            remaining = n_rolls - len(results)
        if len(results) >= n_rolls:
            return results[:n_rolls]
        # else fall through to software fallback for remaining

    # Software fallback (secrets)
    while len(results) < n_rolls:
        bitval = secrets.randbelow(max_val)
        if bitval < 6:
            results.append(bitval + 1)
    return results

# ------------------ GUI ------------------

class QuantumDiceGUI:
    def __init__(self, root):
        self.root = root
        root.title("Quantum Dice — Multi-Qubit Random Number Game")
        root.geometry("560x420")
        root.resizable(False, False)

        # Style
        self.mainframe = ttk.Frame(root, padding=12)
        self.mainframe.pack(fill=tk.BOTH, expand=True)

        # Top: Mode selection
        top_row = ttk.Frame(self.mainframe)
        top_row.pack(fill=tk.X, pady=(0,10))

        ttk.Label(top_row, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="quantum" if AER_AVAILABLE else "local")
        self.mode_combo = ttk.Combobox(top_row, textvariable=self.mode_var, values=("quantum", "local"), width=12, state="readonly")
        self.mode_combo.pack(side=tk.LEFT, padx=(8, 12))
        if not AER_AVAILABLE:
            self.mode_combo.set("local")
            self.mode_combo.config(state="disabled")

        ttk.Label(top_row, text="Qubits:").pack(side=tk.LEFT)
        self.qubits_var = tk.IntVar(value=3)
        self.qubits_spin = ttk.Spinbox(top_row, from_=1, to=6, textvariable=self.qubits_var, width=4)
        self.qubits_spin.pack(side=tk.LEFT, padx=(6,12))

        ttk.Label(top_row, text="Shots (batch):").pack(side=tk.LEFT)
        self.shots_var = tk.IntVar(value=1024)
        self.shots_entry = ttk.Entry(top_row, width=8, textvariable=self.shots_var)
        self.shots_entry.pack(side=tk.LEFT, padx=(6,12))

        # Middle: Result & buttons
        middle = ttk.Frame(self.mainframe)
        middle.pack(fill=tk.X)

        self.result_label = ttk.Label(middle, text="Roll result: —", font=(None, 20))
        self.result_label.pack(pady=(6,12))

        btn_row = ttk.Frame(self.mainframe)
        btn_row.pack()

        self.roll_button = ttk.Button(btn_row, text="Roll Once", command=self.roll_once)
        self.roll_button.pack(side=tk.LEFT, padx=8)

        self.roll_many_button = ttk.Button(btn_row, text="Roll Many (batch)", command=self.roll_many_prompt)
        self.roll_many_button.pack(side=tk.LEFT, padx=8)

        self.hist_button = ttk.Button(btn_row, text="Show Histogram", command=self.show_histogram)
        self.hist_button.pack(side=tk.LEFT, padx=8)

        self.clear_button = ttk.Button(btn_row, text="Clear History", command=self.clear_history)
        self.clear_button.pack(side=tk.LEFT, padx=8)

        # Bottom: History
        bottom = ttk.Frame(self.mainframe)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(12,0))

        ttk.Label(bottom, text="History (most recent first):").pack(anchor=tk.W)
        self.history_box = tk.Listbox(bottom, height=8)
        self.history_box.pack(fill=tk.BOTH, expand=True)

        # Internal state
        self.history = []  # list of ints (1..6)

    def set_mode(self):
        return self.mode_var.get() == "quantum" and AER_AVAILABLE

    def roll_once(self):
        self.roll_button.config(state=tk.DISABLED)
        self.roll_many_button.config(state=tk.DISABLED)
        threading.Thread(target=self._roll_once_worker, daemon=True).start()

    def _roll_once_worker(self):
        use_aer = self.set_mode()
        n_qubits = int(self.qubits_var.get())
        # For dice we need at least 3 qubits to cover 6 values. If user sets fewer, we still do rejection but may be infinite; block lower bound to 3.
        if n_qubits < 3:
            n_qubits = 3
        try:
            val = quantum_roll_one_rejection(n_qubits=n_qubits, use_aer=use_aer)
        except Exception as e:
            print("Roll failed:", e)
            val = None
        if val is None:
            self.root.after(0, lambda: messagebox.showerror("Error", "Could not generate roll."))
            self.root.after(0, lambda: self.roll_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.roll_many_button.config(state=tk.NORMAL))
            return
        self.history.insert(0, val)
        self.root.after(0, lambda: self.update_ui_with_result(val))

    def update_ui_with_result(self, val):
        self.result_label.config(text=f"Roll result: {val}")
        self.history_box.insert(0, f"{time.strftime('%H:%M:%S')} — {val}")
        self.roll_button.config(state=tk.NORMAL)
        self.roll_many_button.config(state=tk.NORMAL)

    def roll_many_prompt(self):
        # read shots var and run batch
        try:
            shots = int(self.shots_var.get())
        except Exception:
            messagebox.showerror("Input error", "Shots must be an integer.")
            return
        if shots <= 0 or shots > 200000:
            messagebox.showerror("Input error", "Shots must be between 1 and 200000.")
            return
        self.roll_many_button.config(state=tk.DISABLED)
        self.roll_button.config(state=tk.DISABLED)
        threading.Thread(target=self._roll_many_worker, args=(shots,), daemon=True).start()

    def _roll_many_worker(self, shots):
        use_aer = self.set_mode()
        n_qubits = int(self.qubits_var.get())
        if n_qubits < 3:
            n_qubits = 3
        try:
            results = batch_rolls(shots, n_qubits=n_qubits, use_aer=use_aer)
        except Exception as e:
            print("Batch roll failed:", e)
            results = []
        # prepend to history (most recent first)
        for r in reversed(results):
            self.history.insert(0, r)
        # limit history size
        self.history = self.history[:500]
        self.root.after(0, lambda: self.on_batch_complete(results))

    def on_batch_complete(self, results):
        self.roll_many_button.config(state=tk.NORMAL)
        self.roll_button.config(state=tk.NORMAL)
        if results:
            # show last result
            last = results[-1]
            self.result_label.config(text=f"Last roll: {last} (from batch)")
            # update listbox
            self.history_box.delete(0, tk.END)
            for item in self.history:
                self.history_box.insert(tk.END, f"{item}")
        else:
            messagebox.showerror("Error", "Batch roll failed or returned no results.")

    def show_histogram(self):
        # build counts from history; if history empty, ask user for number of shots
        if not self.history:
            messagebox.showinfo("No data", "No history available. Please roll first or set a Shots value and click 'Roll Many'.")
            return
        counts = Counter(self.history)
        labels = [1,2,3,4,5,6]
        freqs = [counts.get(x, 0) for x in labels]
        plt.figure(figsize=(7,4))
        plt.bar(labels, freqs)
        plt.xticks(labels)
        plt.xlabel('Die face')
        plt.ylabel('Frequency')
        plt.title('Dice roll distribution')
        plt.tight_layout()
        plt.show()

    def clear_history(self):
        self.history.clear()
        self.history_box.delete(0, tk.END)
        self.result_label.config(text="Roll result: —")

# ------------------ Run ------------------

def main():
    root = tk.Tk()
    app = QuantumDiceGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
