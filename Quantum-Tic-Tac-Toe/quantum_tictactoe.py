import tkinter as tk
import random
from qiskit import QuantumCircuit, transpile
try:
    from qiskit_aer import AerSimulator
    AER_AVAILABLE = True
except ImportError:
    AER_AVAILABLE = False

root = tk.Tk()
root.title("Quantum Tic-Tac-Toe")
root.geometry("400x500")

qc = QuantumCircuit(9)
buttons = []
player_turn = True
clicked_cells = [False] * 9

def quantum_random_bit():
    try:
        if AER_AVAILABLE:
            sim = AerSimulator()
            q = QuantumCircuit(1, 1)
            q.h(0)
            q.measure_all()
            tqc = transpile(q, sim)
            result = sim.run(tqc, shots=1).result()
            counts = result.get_counts()
            bit = list(counts.keys())[0]
            return int(bit)
        else:
            raise Exception("Aer not available")
    except Exception:
        return random.randint(0, 1)

def quantum_move(index):
    global player_turn
    if clicked_cells[index]:
        return
    clicked_cells[index] = True

    if player_turn:
        buttons[index].config(text="X", fg="blue")
    else:
        buttons[index].config(text="O", fg="red")

    qc.h(index)  # Apply quantum superposition
    player_turn = not player_turn
    update_status()

def collapse_board():
    global clicked_cells
    # Try quantum measurement, fallback to random
    try:
        if AER_AVAILABLE:
            sim = AerSimulator()
            tqc = transpile(qc, sim)
            result = sim.run(tqc, shots=1).result()
            counts = result.get_counts()
            outcome = list(counts.keys())[0][::-1]
        else:
            raise Exception("Aer not available")
    except Exception:
        outcome = ''.join(random.choice('01') for _ in range(9))

    for i, val in enumerate(outcome):
        if val == '1':
            buttons[i].config(text='O', fg="red", state="disabled")
        else:
            buttons[i].config(text='X', fg="blue", state="disabled")

    clicked_cells = [True] * 9  # board is now full
    check_win()

def update_status():
    status_label.config(text=f"Player {'X' if player_turn else 'O'}'s turn")

def check_win():
    lines = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    x_win = o_win = False
    for line in lines:
        a, b, c = [buttons[i]['text'] for i in line]
        if a == b == c and a != "":
            if a == "X":
                x_win = True
            elif a == "O":
                o_win = True

    if x_win and o_win:
        qbit = quantum_random_bit()
        winner = 'X' if qbit == 0 else 'O'
        status_label.config(text=f"Quantum tie! Collapsed randomly to Player {winner} wins!")
    elif x_win:
        status_label.config(text="Player X wins!")
    elif o_win:
        status_label.config(text="Player O wins!")
    elif all([buttons[i]['text'] != "" for i in range(9)]):
        status_label.config(text="It's a draw!")
    else:
        status_label.config(text="No winner yet — keep playing!")

    if x_win or o_win:
        for btn in buttons:
            btn.config(state="disabled")

frame = tk.Frame(root)
frame.pack(pady=20)

for i in range(9):
    b = tk.Button(frame, text="", font=("Arial", 32), width=5, height=2,
                  command=lambda i=i: quantum_move(i))
    b.grid(row=i//3, column=i%3, padx=5, pady=5)
    buttons.append(b)

collapse_btn = tk.Button(root, text="Collapse Board", font=("Arial", 14),
                         command=collapse_board, bg="yellow", width=20)
collapse_btn.pack(pady=20)

status_label = tk.Label(root, text="Player X's turn", font=("Arial", 16))
status_label.pack()

root.mainloop()
