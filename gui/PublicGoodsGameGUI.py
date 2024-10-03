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

    def update(self):
        # Aktualisiere den Namen des aktuellen Agenten
        current_agent = self.simulation.agent_list[0]
        self.current_agent_label.config(text=f"Agent: {current_agent.name}")

        # Aktualisiere die Agentenliste (Reward/Punish)
        self.update_agent_list()

        # Aktualisiere andere GUI-Elemente, falls notwendig
        self.update_history_display()

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
        self.history_inner_frame_id = self.history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor='nw')

        # Configure scrolling behavior
        self.history_inner_frame.bind("<Configure>", lambda event: self.history_canvas.configure(
            scrollregion=self.history_canvas.bbox("all")))

        # Title for History
        self.history_title_label = tk.Label(
            self.history_inner_frame,
            text="History",
            fg="white",
            bg='black',
            font=("Helvetica", 16)
        )
        self.history_title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    def setup_right_control_frame(self):
        # Right frame for agent list and controls
        self.control_frame = tk.Frame(self.root, bg='#171717', width=300)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Agent List Title
        self.agent_list_title = tk.Label(
            self.control_frame,
            text="Agent List",
            fg="white",
            bg='#171717',
            font=("Helvetica", 16)
        )
        self.agent_list_title.pack(pady=10)

        # Display current agent's name
        current_agent = self.simulation.agent_list[0]
        self.current_agent_label = tk.Label(
            self.control_frame,
            text=f"Agent: {current_agent.name}",
            fg="white",
            bg='#171717',
            font=("Helvetica", 12)
        )
        self.current_agent_label.pack(pady=5)

        # Contribute Section
        self.contribute_label = tk.Label(
            self.control_frame,
            text="Contribute for Current Agent:",
            fg="white",
            bg='#171717',
            font=("Helvetica", 14)
        )
        self.contribute_label.pack(pady=10)

        self.contribute_entry = tk.Entry(self.control_frame, width=15)
        self.contribute_entry.pack(pady=5)

        # Reward Section
        self.reward_label = tk.Label(
            self.control_frame,
            text="Select Agent to Reward",
            fg="white",
            bg='#171717',
            font=("Helvetica", 14)
        )
        self.reward_label.pack(pady=10)

        self.reward_listbox = tk.Listbox(
            self.control_frame,
            bg='#171717',
            fg="white",
            font=("Helvetica", 12),
            selectmode=tk.SINGLE,
            exportselection=False,  # Preserve selection across multiple listboxes
            height=5
        )
        self.reward_listbox.pack(pady=5)

        # Punish Section
        self.punish_label = tk.Label(
            self.control_frame,
            text="Select Agent to Punish",
            fg="white",
            bg='#171717',
            font=("Helvetica", 14)
        )
        self.punish_label.pack(pady=10)

        self.punish_listbox = tk.Listbox(
            self.control_frame,
            bg='#171717',
            fg="white",
            font=("Helvetica", 12),
            selectmode=tk.SINGLE,
            exportselection=False,  # Preserve selection across multiple listboxes
            height=5
        )
        self.punish_listbox.pack(pady=5)

        # Bindings für die Auswahl
        self.reward_listbox.bind('<<ListboxSelect>>', self.handle_selection)
        self.punish_listbox.bind('<<ListboxSelect>>', self.handle_selection)

        # Submit Button
        self.submit_button = tk.Button(
            self.control_frame,
            text="Submit",
            command=self.submit_action,
            width=15,
            bg="green",
            fg="white"
        )
        self.submit_button.pack(pady=20)

        # Aktualisiere die Anzeige mit verfügbaren Agenten
        self.update_agent_list()

    def handle_selection(self, event):
        """
        Diese Methode verarbeitet die Auswahl in den Listboxen und stellt sicher,
        dass die Agenten für Reward und Punish korrekt ausgewählt und abgewählt werden können.
        """
        widget = event.widget
        if widget.curselection():
            index = widget.curselection()[0]
            # Highlight die Auswahl, aber tue nichts anderes. Listbox verwaltet den Zustand.
            widget.activate(index)

    def update_agent_list(self):
        # Ermittelt den aktuellen Agenten
        current_agent = self.simulation.agent_list[0]

        # Ruft das Dictionary des aktuellen Agenten ab
        current_agent_dictionary = current_agent.get_agent_dictionary()

        # Leert die Reward und Punish Listbox
        self.reward_listbox.delete(0, tk.END)
        self.punish_listbox.delete(0, tk.END)

        # Erstellt eine Zuordnung von Namen zu Schlüsseln
        self.agent_key_map = {}

        # Zeigt alle Agenten an, deren Schlüssel nicht 'A' ist
        for key, agent in current_agent_dictionary.items():
            if key != 'A':
                # Speichere die Zuordnung von Name zu Schlüssel
                self.agent_key_map[agent.name] = key

                # Füge den Agentennamen zur Reward- und Punish-Listbox hinzu
                self.reward_listbox.insert(tk.END, agent.name)
                self.punish_listbox.insert(tk.END, agent.name)

    def get_reward_selection(self):
        # Holt die Auswahl aus der Reward Listbox
        selected_indices = self.reward_listbox.curselection()
        if selected_indices:
            selected_name = self.reward_listbox.get(selected_indices[0])
            # Gibt den entsprechenden Schlüssel (key) statt des Namens zurück
            return self.agent_key_map[selected_name]
        return "Z"  # Default-Wert, falls kein Agent ausgewählt wurde

    def get_punish_selection(self):
        # Holt die Auswahl aus der Punish Listbox
        selected_indices = self.punish_listbox.curselection()
        if selected_indices:
            selected_name = self.punish_listbox.get(selected_indices[0])
            # Gibt den entsprechenden Schlüssel (key) statt des Namens zurück
            return self.agent_key_map[selected_name]
        return "Z"  # Default-Wert, falls kein Agent ausgewählt wurde

    def submit_action(self):
        # Diese Methode sammelt die Eingaben und sendet sie an die Spielumgebung
        contribute_value = self.get_contribute_value()
        reward_selection = self.get_reward_selection() or "Z"  # Setze "Z", wenn nichts ausgewählt wurde
        punish_selection = self.get_punish_selection() or "Z"  # Setze "Z", wenn nichts ausgewählt wurde

        # Validierung der Eingaben
        if contribute_value < 0:
            print("Der Beitrag muss eine positive Zahl sein.")
            return

        # Verhindere, dass der Spieler denselben Agenten für Reward und Punish auswählt
        if reward_selection == punish_selection and reward_selection != "Z":
            print("Der gleiche Agent kann nicht belohnt und bestraft werden.")
            return

        current_agent = self.simulation.agent_list[0]

        # Erstelle die Eingabesequenz
        input_sequence = [
            "C",  # Contribute für den aktuellen Agenten
            str(contribute_value),
            "R",  # Reward
            reward_selection,  # Reward target
            "P",  # Punish
            punish_selection  # Punish target
        ]

        # Sende die Eingaben an die Spielumgebung und übergebe den Agenten
        self.simulation.manual_input_controller.handle_input(input_sequence, current_agent)

        # Setze das submit_waiting-Flag, um den nächsten Schritt zu starten
        self.simulation.submit_waiting.set(True)

        # Optional: Leere die Eingabefelder nach dem Submit
        self.contribute_entry.delete(0, tk.END)
        self.reward_listbox.selection_clear(0, tk.END)
        self.punish_listbox.selection_clear(0, tk.END)

    def get_contribute_value(self):
        # Holt den Beitragwert aus dem Eingabefeld
        try:
            contribute_value = int(self.contribute_entry.get())
            if contribute_value < 0:
                raise ValueError
            return contribute_value
        except ValueError:
            print("Bitte geben Sie eine gültige positive Zahl für den Beitrag ein.")
            return -1  # Ungültiger Wert

    def update_history_display(self):
        # Aktualisiert das History-Panel mit neuen Daten (falls vorhanden)
        pass

    def update_history(self, round_num, contributions, nomination_matrix):
        # Update the history frame with new round data
        round_label = tk.Label(
            self.history_inner_frame,
            text=f"Round {round_num}",
            fg="white",
            bg='black',
            font=("Helvetica", 12)
        )
        round_label.grid(row=round_num, column=0, padx=10, pady=5)

        # Display contributions of agents
        contribution_label = tk.Label(
            self.history_inner_frame,
            text=f"Contributions: {contributions}",
            fg="white",
            bg='black',
            font=("Helvetica", 12)
        )
        contribution_label.grid(row=round_num, column=1, padx=10, pady=5)

        # Display nomination matrix
        matrix_frame = tk.Frame(self.history_inner_frame, bg='black')
        matrix_frame.grid(row=round_num, column=2, padx=10, pady=5)
        self.draw_matrix(matrix_frame, nomination_matrix)

    def draw_matrix(self, parent_frame, matrix):
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                cell_text = val if val else " "
                cell_label = tk.Label(
                    parent_frame,
                    text=cell_text,
                    fg="white",
                    bg='#171717',
                    relief='solid',
                    borderwidth=1,
                    width=4,
                    height=2
                )
                cell_label.grid(row=i, column=j, padx=1, pady=1)
