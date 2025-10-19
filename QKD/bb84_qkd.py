# BB84 Quantum Key Distribution + Secure Message GUI
import tkinter as tk
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random

# ----------------------------
# Functions for BB84 & encryption
# ----------------------------
def encode_bit(bit, basis):
    qc = QuantumCircuit(1, 1)
    if basis == 'X':
        qc.h(0)
    if bit == 1:
        qc.x(0)
    return qc

def run_bb84(message):
    num_bits = 8
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    alice_qubits = [encode_bit(bit, basis) for bit, basis in zip(alice_bits, alice_bases)]

    bob_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    bob_results = []

    sim = AerSimulator()
    for qc, basis in zip(alice_qubits, bob_bases):
        if basis == 'X':
            qc.h(0)
        qc.measure(0, 0)
        result = sim.run(qc).result()
        measured_bit = int(list(result.get_counts().keys())[0])
        bob_results.append(measured_bit)

    shared_key = [b for a, b, ab in zip(alice_bits, bob_results, zip(alice_bases, bob_bases)) if ab[0] == ab[1]]

    # Convert message to bits
    message_bits = [int(b) for c in message for b in format(ord(c), '08b')]

    # Prepare key for message
    key_for_message = (shared_key * ((len(message_bits)//len(shared_key)) + 1))[:len(message_bits)]

    # Encrypt & decrypt
    cipher_bits = [m ^ k for m, k in zip(message_bits, key_for_message)]
    decrypted_bits = [c ^ k for c, k in zip(cipher_bits, key_for_message)]
    decrypted_message = ''.join(chr(int(''.join(map(str, decrypted_bits[i:i+8])), 2)) for i in range(0, len(decrypted_bits), 8))

    return alice_bits, alice_bases, bob_bases, bob_results, shared_key, cipher_bits, decrypted_message

# ----------------------------
# GUI setup
# ----------------------------
def run_simulation():
    message = entry_message.get()
    if not message:
        status_label.config(text="Enter a message to send.")
        return
    results = run_bb84(message)
    alice_bits, alice_bases, bob_bases, bob_results, shared_key, cipher_bits, decrypted_message = results

    output_text = f"""
Alice bits:    {alice_bits}
Alice bases:   {alice_bases}
Bob bases:     {bob_bases}
Bob results:   {bob_results}
Shared key:    {shared_key}
Encrypted bits:{cipher_bits}
Decrypted msg: {decrypted_message}
"""
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, output_text)
    status_label.config(text="Simulation complete!")

# GUI elements
root = tk.Tk()
root.title("BB84 Quantum Key Distribution Simulator")
root.geometry("700x500")
root.configure(bg="#101820")

title_label = tk.Label(root, text="BB84 Quantum Key Distribution + Secure Message", fg="white", bg="#101820", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

entry_label = tk.Label(root, text="Enter message to send:", fg="white", bg="#101820", font=("Arial", 12))
entry_label.pack()
entry_message = tk.Entry(root, width=30, justify="center")
entry_message.pack(pady=5)

run_button = tk.Button(root, text="Run Simulation", command=run_simulation, bg="#4e9af1", fg="white", font=("Arial", 12, "bold"))
run_button.pack(pady=10)

status_label = tk.Label(root, text="", fg="yellow", bg="#101820", font=("Arial", 12, "italic"))
status_label.pack(pady=5)

text_output = tk.Text(root, height=20, width=80)
text_output.pack(pady=10)

root.mainloop()
