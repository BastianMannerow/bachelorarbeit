import tkinter as tk
from tkinter import ttk


class PublicGoodsGameGUI:
    def __init__(self, simulation, public_goods_game_environment, root):
        self.simulation = simulation
        self.public_goods_game_environment = public_goods_game_environment
        self.root = root
        self.root.title("Social Simulation")
        self.root.configure(bg='black')
        self.root.state('zoomed')

        # Layout: Left for History, Right for Agent List and Controls
        self.setup_left_history_frame()
        self.setup_right_control_frame()

    def setup_left_history_frame(self):
        # Left frame to display history
        self.history_frame = tk.Frame(self.root, bg='black')
        self.history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollable canvas
        self.history_canvas = tk.Canvas(self.history_frame, bg='black', highlightthickness=0)
        self.history_scrollbar = tk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame inside the canvas to hold the round history
        self.history_inner_frame = tk.Frame(self.history_canvas, bg='black')
        self.history_inner_frame_id = self.history_canvas.create_window((0, 0), window=self.history_inner_frame,
                                                                        anchor='nw')

        # Configure scrolling behavior
        self.history_inner_frame.bind("<Configure>", lambda event: self.history_canvas.configure(
            scrollregion=self.history_canvas.bbox("all")))

        # Title for History
        self.history_title_label = tk.Label(self.history_inner_frame, text="History", fg="white", bg='black',
                                            font=("Helvetica", 16))
        self.history_title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    def setup_right_control_frame(self):
        # Right frame for agent list and controls
        self.control_frame = tk.Frame(self.root, bg='#171717', width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Agent List Title
        self.agent_list_title = tk.Label(self.control_frame, text="Agent List", fg="white", bg='#171717',
                                         font=("Helvetica", 16))
        self.agent_list_title.pack(pady=10)

        # Agent List
        self.agent_listbox = tk.Listbox(self.control_frame, bg='#171717', fg="white", font=("Helvetica", 12), height=8)
        self.agent_listbox.pack(pady=10)

        # Add agents to the listbox
        self.update_agent_list()

        # Contribute, Punish, Reward Options
        self.control_label = tk.Label(self.control_frame, text="Actions", fg="white", bg='#171717',
                                      font=("Helvetica", 16))
        self.control_label.pack(pady=10)

        self.contribute_button = tk.Button(self.control_frame, text="Contribute", command=self.select_contribute,
                                           width=15)
        self.contribute_button.pack(pady=5)

        self.punish_button = tk.Button(self.control_frame, text="Punish", command=self.select_punish, width=15)
        self.punish_button.pack(pady=5)

        self.reward_button = tk.Button(self.control_frame, text="Reward", command=self.select_reward, width=15)
        self.reward_button.pack(pady=5)

        # Submit Button
        self.submit_button = tk.Button(self.control_frame, text="Submit", command=self.submit_action, width=15,
                                       bg="green", fg="white")
        self.submit_button.pack(pady=20)

    def select_contribute(self):
        # Placeholder for contributing action
        print("Contribute selected")

    def select_punish(self):
        # Placeholder for punishing action
        print("Punish selected")

    def select_reward(self):
        # Placeholder for rewarding action
        print("Reward selected")

    def submit_action(self):
        # Placeholder for submitting action
        print("Submit action")

    def update(self):
        # Aktualisiert die GUI-Elemente
        self.update_agent_list()
        # Hier können andere GUI-Elemente aktualisiert werden (z.B. Historie)
        self.update_history_display()

    def update_agent_list(self):
        # Aktualisiert die Liste der Agenten
        self.agent_listbox.delete(0, tk.END)  # Löscht die aktuelle Liste
        for agent in self.public_goods_game_environment.agent_list:
            self.agent_listbox.insert(tk.END, agent.name)  # Fügt die Agenten erneut hinzu

    def update_history_display(self):
        # Aktualisiere das History-Panel mit neuen Daten (wenn vorhanden)
        pass

    def update_history(self, round_num, contributions, nomination_matrix):
        # Update the history frame with new round data
        round_label = tk.Label(self.history_inner_frame, text=f"Round {round_num}", fg="white", bg='black',
                               font=("Helvetica", 12))
        round_label.grid(row=round_num, column=0, padx=10, pady=5)

        # Display contributions of agents
        contribution_label = tk.Label(self.history_inner_frame, text=f"Contributions: {contributions}", fg="white",
                                      bg='black', font=("Helvetica", 12))
        contribution_label.grid(row=round_num, column=1, padx=10, pady=5)

        # Display nomination matrix
        matrix_frame = tk.Frame(self.history_inner_frame, bg='black')
        matrix_frame.grid(row=round_num, column=2, padx=10, pady=5)
        self.draw_matrix(matrix_frame, nomination_matrix)

    def draw_matrix(self, parent_frame, matrix):
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                cell_text = val if val else " "
                cell_label = tk.Label(parent_frame, text=cell_text, fg="white", bg='#171717', relief='solid',
                                      borderwidth=1, width=4, height=2)
                cell_label.grid(row=i, column=j, padx=1, pady=1)
