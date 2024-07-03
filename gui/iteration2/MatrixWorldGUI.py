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
        self.root.title("Social Simulation")
        self.root.configure(bg='black')  # Set window background to black
        self.root.state('zoomed')  # Maximize window

        # Calculate dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        info_frame_width = screen_width // 5

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.info_frame = tk.Frame(self.root, width=info_frame_width, bg='#171717')
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_frame.pack_propagate(False)  # Prevent the frame from resizing

        self.agent_info_frame = tk.Frame(self.info_frame, bg='#171717')
        self.agent_info_frame.pack(padx=10, pady=10)

        self.agent_image_label = tk.Label(self.agent_info_frame, bg='#171717')
        self.agent_image_label.pack(side=tk.LEFT)

        self.agent_name_label = tk.Label(self.agent_info_frame, fg="white", bg='#171717',
                                         font=("Helvetica", 16, "bold"))
        self.agent_name_label.pack(side=tk.LEFT, padx=10)

        self.visual_stimuli_title = tk.Label(self.info_frame, text="Visuelle Stimuli", fg="white", bg='#171717',
                                             font=("Helvetica", 14))
        self.visual_stimuli_title.pack(padx=10, pady=10)

        self.visual_stimuli_frame = tk.Frame(self.info_frame, bg='#171717')
        self.visual_stimuli_frame.pack(padx=10, pady=10)

        self.cell_size = 40  # Size of each cell in the grid
        # Dictionary to keep references to Images
        self.agent_images = {}
        self.agent_gifs = {}
        self.food_images = {}
        self.environment_images = {
            "grass": self.load_environment_image("gui/iteration2/sprites/environment/grass.png"),
            "tree": self.load_environment_image("gui/iteration2/sprites/environment/tree.png")
        }

        # Select a random agent initially
        self.selected_agent = random.choice(
            [agent for row in self.world.level_matrix for cell in row for agent in cell if
             isinstance(agent, AgentBuilder)])
        self.update_info_panel(self.selected_agent)

        # Add scrollbars but keep them invisible
        self.h_scroll = tk.Scrollbar(self.canvas, orient=tk.HORIZONTAL, command=self.canvas.xview, width=0)
        self.v_scroll = tk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.canvas.yview, width=0)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        # Bind arrow keys for scrolling
        self.root.bind("<Left>", lambda event: self.canvas.xview_scroll(-1, "units"))
        self.root.bind("<Right>", lambda event: self.canvas.xview_scroll(1, "units"))
        self.root.bind("<Up>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.root.bind("<Down>", lambda event: self.canvas.yview_scroll(1, "units"))

        # Bind mouse click to select agent
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Schedule visual stimuli updates every second
        self.schedule_visual_stimuli_update()

    def load_environment_image(self, path):
        image = Image.open(path)
        image.thumbnail((self.cell_size, self.cell_size), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def get_random_food_image(self):
        food_dir = "gui/iteration2/sprites/food"
        food_files = [f for f in os.listdir(food_dir) if f.endswith('.png')]
        random_food_file = random.choice(food_files)
        image_path = os.path.join(food_dir, random_food_file)
        image = Image.open(image_path)
        image.thumbnail((self.cell_size, self.cell_size), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def draw_grid(self):
        self.canvas.delete("all")
        for r, row in enumerate(self.world.level_matrix):
            for c, cell in enumerate(row):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_image(x1, y1, anchor=tk.NW,
                                         image=self.environment_images["grass"])  # Always draw grass first
                if any(isinstance(obj, Wall) for obj in cell):
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.environment_images["tree"])
                elif any(isinstance(obj, Food) for obj in cell):
                    food_obj = next(obj for obj in cell if isinstance(obj, Food))
                    self.draw_food(food_obj, x1, y1)
                for obj in cell:
                    if isinstance(obj, AgentBuilder):
                        self.draw_agent(obj, x1, y1)

        self.draw_red_overlay()  # Draw the red overlay around the selected agent

        # Update canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def draw_red_overlay(self):
        if not self.selected_agent:
            return

        agent_x, agent_y = self.find_agent_position(self.selected_agent)
        if agent_x is None or agent_y is None:
            return

        overlay_color = "#2e1111"

        for dx in range(-2, 3):
            for dy in range(-2, 3):
                x = agent_x + dx
                y = agent_y + dy
                if 0 <= x < len(self.world.level_matrix[0]) and 0 <= y < len(self.world.level_matrix):
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    # Simulate transparency by creating multiple overlapping rectangles with varying opacities
                    for i in range(10):  # Create 10 overlapping rectangles to simulate transparency
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=overlay_color, outline="", stipple="gray50")

    def find_agent_position(self, agent):
        for r, row in enumerate(self.world.level_matrix):
            for c, cell in enumerate(row):
                if agent in cell:
                    return c, r
        return None, None

    def draw_food(self, food, x, y):
        if food not in self.food_images:
            self.food_images[food] = self.get_random_food_image()
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.food_images[food])

    def draw_agent(self, agent, x, y):
        gif_path = f"gui/iteration2/sprites/pokemon/gif/{agent.get_name_number()}.gif"
        if gif_path not in self.agent_gifs:
            image = Image.open(gif_path)
            frames = [ImageTk.PhotoImage(frame.resize((self.cell_size, self.cell_size), Image.LANCZOS)) for frame in
                      ImageSequence.Iterator(image)]
            self.agent_gifs[gif_path] = frames
            self.agent_images[gif_path] = 0  # Start at the first frame
        frames = self.agent_gifs[gif_path]
        frame_index = self.agent_images[gif_path]
        self.canvas.create_image(x, y, anchor=tk.NW, image=frames[frame_index])
        self.agent_images[gif_path] = (frame_index + 1) % len(frames)  # Loop through frames

    def update_info_panel(self, agent):
        png_path = f"gui/iteration2/sprites/pokemon/png/{agent.get_name_number()}.png"
        image = Image.open(png_path)
        image.thumbnail((100, 100), Image.LANCZOS)
        agent_image = ImageTk.PhotoImage(image)
        self.agent_image_label.config(image=agent_image)
        self.agent_image_label.image = agent_image

        self.agent_name_label.config(text=agent.get_agent_name())

        for widget in self.visual_stimuli_frame.winfo_children():
            widget.destroy()

        visual_stimuli = agent.get_visual_stimuli()
        self.draw_matrix(visual_stimuli)

    def on_canvas_click(self, event):
        # Adjust click coordinates based on scroll position
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        r, c = int(y // self.cell_size), int(x // self.cell_size)
        if r < len(self.world.level_matrix) and c < len(self.world.level_matrix[0]):
            for obj in self.world.level_matrix[r][c]:
                if isinstance(obj, AgentBuilder):
                    self.selected_agent = obj
                    self.update_info_panel(self.selected_agent)
                    break

    def update(self):
        self.draw_grid()
        self.root.update_idletasks()
        self.root.update()
        self.root.after(50, self.update)  # Repeat update every 50 ms

    def draw_matrix(self, matrix):
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                cell_text = val if val else " "
                cell_label = tk.Label(self.visual_stimuli_frame, text=cell_text, fg="white", bg='#171717', relief='solid',
                                      borderwidth=1, width=4, height=2, highlightbackground="white", highlightcolor="white", highlightthickness=1)
                cell_label.grid(row=i, column=j, padx=1, pady=1)

    def schedule_visual_stimuli_update(self):
        self.update_info_panel(self.selected_agent)
        self.root.after(1000, self.schedule_visual_stimuli_update)  # Schedule every second

