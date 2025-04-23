import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageTk

# Function to render the chess board based on a 2D array state
def render_chess_board(board_state, output_path):
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ["#F0D9B5", "#B58863"]

    for x in range(8):
        for y in range(8):
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[(x + y) % 2]))

    for y in range(8):
        for x in range(8):
            piece = board_state[7 - y][x]
            if piece != ".":
                ax.text(x + 0.5, y + 0.5, piece, fontsize=24, ha='center', va='center')

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal', adjustable='box')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

# GUI Logic
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Chess GUI")
        self.board_state = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]
        self.selected = None
        self.image_label = tk.Label(self.root)
        self.image_label.pack()
        self.update_board()
        self.image_label.bind("<Button-1>", self.on_click)

    def update_board(self):
        render_chess_board(self.board_state, "chess_board_gui.png")
        img = Image.open("chess_board_gui.png")
        img = img.resize((480, 480), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

    def on_click(self, event):
        x = event.x // 60
        y = 7 - (event.y // 60)
        if self.selected:
            from_x, from_y = self.selected
            piece = self.board_state[from_y][from_x]
            self.board_state[from_y][from_x] = "."
            self.board_state[y][x] = piece
            self.selected = None
        else:
            if self.board_state[y][x] != ".":
                self.selected = (x, y)
        self.update_board()

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
