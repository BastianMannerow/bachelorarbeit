import tkinter as tk
from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall
from agents.iteration2.Agent import Agent

class MatrixWorldGUI:
    def __init__(self, world, root):
        self.world = world
        self.root = root
        self.canvas = tk.Canvas(self.root, width=900, height=900)
        self.canvas.pack()
        self.cell_size = 40  # Size of each cell in the grid

    def draw_grid(self):
        self.canvas.delete("all")
        for r, row in enumerate(self.world.level_matrix):
            for c, cell in enumerate(row):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if any(isinstance(obj, Wall) for obj in cell):
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                elif any(isinstance(obj, Food) for obj in cell):
                    self.canvas.create_oval(x1, y1, x2, y2, fill="green")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")
                if any(isinstance(obj, Agent) for obj in cell):
                    self.canvas.create_oval(x1, y1, x2, y2, fill="red")

    def update(self):
        self.draw_grid()
        self.root.update_idletasks()
        self.root.update()
