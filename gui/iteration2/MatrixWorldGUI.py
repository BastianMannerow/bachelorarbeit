import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os
import random
from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall
from agents.iteration2.AgentBuilder import AgentBuilder

class MatrixWorldGUI:
    def __init__(self, world, root):
        self.world = world
        self.root = root
        self.canvas = tk.Canvas(self.root, width=900, height=900)
        self.canvas.pack()
        self.cell_size = 40  # Size of each cell in the grid
        self.agent_images = {}  # Dictionary to keep references to agent images
        self.agent_gifs = {}    # Dictionary to keep references to GIF frames
        self.food_images = {}   # Dictionary to keep references to food images
        self.environment_images = {
            "grass": self.load_environment_image("gui/iteration2/sprites/environment/grass.png"),
            "tree": self.load_environment_image("gui/iteration2/sprites/environment/tree.png")
        }

    def load_environment_image(self, path):
        image = Image.open(path).resize((self.cell_size, self.cell_size))
        return ImageTk.PhotoImage(image)

    def get_random_food_image(self):
        food_dir = "gui/iteration2/sprites/food"
        food_files = [f for f in os.listdir(food_dir) if f.endswith('.png')]
        random_food_file = random.choice(food_files)
        image_path = os.path.join(food_dir, random_food_file)
        image = Image.open(image_path).resize((self.cell_size, self.cell_size))
        return ImageTk.PhotoImage(image)

    def draw_grid(self):
        self.canvas.delete("all")
        for r, row in enumerate(self.world.level_matrix):
            for c, cell in enumerate(row):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.environment_images["grass"])  # Always draw grass first
                if any(isinstance(obj, Wall) for obj in cell):
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.environment_images["tree"])
                elif any(isinstance(obj, Food) for obj in cell):
                    food_obj = next(obj for obj in cell if isinstance(obj, Food))
                    self.draw_food(food_obj, x1, y1)
                for obj in cell:
                    if isinstance(obj, AgentBuilder):
                        self.draw_agent(obj, x1, y1)

    def draw_food(self, food, x, y):
        if food not in self.food_images:
            self.food_images[food] = self.get_random_food_image()
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.food_images[food])

    def draw_agent(self, agent, x, y):
        gif_path = f"gui/iteration2/sprites/pokemon/gif/{agent.get_name_number()}.gif"
        if gif_path not in self.agent_gifs:
            image = Image.open(gif_path)
            frames = [ImageTk.PhotoImage(frame.resize((self.cell_size, self.cell_size))) for frame in ImageSequence.Iterator(image)]
            self.agent_gifs[gif_path] = frames
            self.agent_images[gif_path] = 0  # Start at the first frame
        frames = self.agent_gifs[gif_path]
        frame_index = self.agent_images[gif_path]
        self.canvas.create_image(x, y, anchor=tk.NW, image=frames[frame_index])
        self.agent_images[gif_path] = (frame_index + 1) % len(frames)  # Loop through frames

    def update(self):
        self.draw_grid()
        self.root.update_idletasks()
        self.root.update()
        self.root.after(100, self.update)  # Repeat update every 100 ms