import tkinter as tk

class HalmaBoardGUI(tk.Tk):
    def __init__(self, board_state):
        super().__init__()

        self.title("Halma Board")

        self.board_state = board_state

        self.canvas = tk.Canvas(self, width=400, height=400, bg="white")
        self.canvas.pack()

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")  # Clear the canvas

        square_size = 400 / len(self.board_state)

        for i in range(len(self.board_state)):
            for j in range(len(self.board_state)):
                x0, y0 = j * square_size, i * square_size
                x1, y1 = x0 + square_size, y0 + square_size

                color = "lightgrey" if self.board_state[i][j] == 0 else \
                        "blue" if self.board_state[i][j] == 1 else \
                        "red"

                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)

                if self.board_state[i][j] != 0:
                    self.canvas.create_oval(x0 + 10, y0 + 10, x1 - 10, y1 - 10, fill=color)

        self.update()  # Force update of the GUI
