import tkinter as tk
from PIL import Image, ImageTk
import os

class PublicGoodsGameGUI:
    def __init__(self, simulation, public_goods_game_environment, root):
        self.simulation = simulation
        self.public_goods_game_environment = public_goods_game_environment
        self.root = root

        self.root.title("Social Simulation")
        self.root.configure(bg='black')
        self.root.state('zoomed')

        # Path to the Icons folder
        self.icons_path = os.path.join(os.path.dirname(__file__), "Icons")

        # Layout: Only top frame for Agent Display
        self.setup_agents_display_frame()

    def update(self):
        # Aktualisiere die Agentenanzeige (nebeneinander)
        self.update_agent_display()

    def setup_agents_display_frame(self):
        # Frame for displaying agents side-by-side
        self.agents_display_frame = tk.Frame(self.root, bg='black')
        self.agents_display_frame.pack(fill=tk.BOTH, expand=True)

        # Configure the root frame for uniform distribution
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Add label for each agent in the simulation agent list
        self.agent_labels = {}

        total_agents = len(self.simulation.agent_list)
        columns = min(total_agents, 4)  # Display up to 4 agents per row for better visibility

        for index, agent in enumerate(self.simulation.agent_list):
            # Create a frame for each agent's label and image
            agent_frame = tk.Frame(self.agents_display_frame, bg='black', padx=20, pady=20)
            row, col = divmod(index, columns)
            agent_frame.grid(row=row, column=col, sticky="nsew", padx=20, pady=20)
            self.agents_display_frame.grid_columnconfigure(col, weight=1, uniform="col")
            self.agents_display_frame.grid_rowconfigure(row, weight=1, uniform="row")

            # Center container for vertical centering of text and image
            center_frame = tk.Frame(agent_frame, bg='black')
            center_frame.pack(expand=True)

            # Label for the agent's name and role
            agent_label = tk.Label(
                center_frame,
                text=agent.name,
                fg="white",
                bg='black',
                font=("Helvetica", 30),  # Larger font size for better visibility
                borderwidth=2,
                relief="solid",
                padx=10,
                pady=10,
                justify="center"
            )
            agent_label.pack(anchor="center")

            self.agent_labels[agent.name] = {
                "frame": center_frame,
                "label": agent_label,
                "image_label": None,  # Placeholder for image label
                "reason_label": None  # Placeholder for reason label
            }

    def update_agent_display(self):
        # Update each agent's label in the display
        for agent in self.simulation.agent_list:
            if agent.name in self.agent_labels:
                self.agent_labels[agent.name]["label"].config(text=agent.name)

    def show_agent_action(self, agent_name, action, reason):
        """Displays the agent's action, an image, and a reason for 4 seconds."""
        if agent_name in self.agent_labels:
            original_text = self.agent_labels[agent_name]["label"].cget("text")
            self.agent_labels[agent_name]["label"].config(text=f"{agent_name}\n({action})")

            # Load the image from the Icons folder and resize to fit the agent area
            try:
                image_path = os.path.join(self.icons_path, f"{action}.png")
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.LANCZOS)  # Double the previous image size
                photo = ImageTk.PhotoImage(image)

                # Add image label below the agent label
                image_label = tk.Label(self.agent_labels[agent_name]["frame"], image=photo, bg='black')
                image_label.image = photo  # Keep reference to avoid garbage collection
                image_label.pack(anchor="center", pady=10)  # Center and add space below the text

                # Add reason label below the image
                reason_label = tk.Label(
                    self.agent_labels[agent_name]["frame"],
                    text=reason,
                    fg="lightgray",
                    bg='black',
                    font=("Helvetica", 18),
                    justify="center"
                )
                reason_label.pack(anchor="center", pady=5)

                # Store labels in the agent's entry
                self.agent_labels[agent_name]["image_label"] = image_label
                self.agent_labels[agent_name]["reason_label"] = reason_label
            except FileNotFoundError:
                print(f"Image for action '{action}' not found in Icons folder")

            # Remove action, image, and reason after 4 seconds
            def reset_action():
                self.agent_labels[agent_name]["label"].config(text=original_text)
                if self.agent_labels[agent_name]["image_label"]:
                    self.agent_labels[agent_name]["image_label"].destroy()
                    self.agent_labels[agent_name]["image_label"] = None
                if self.agent_labels[agent_name]["reason_label"]:
                    self.agent_labels[agent_name]["reason_label"].destroy()
                    self.agent_labels[agent_name]["reason_label"] = None

            self.root.after(4000, reset_action)

    def update_round(self):
        pass
