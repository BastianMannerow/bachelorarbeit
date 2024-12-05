import tkinter as tk


class PublicGoodsGameGUI:
    def __init__(self, simulation, public_goods_game_environment, history, root):
        self.simulation = simulation
        self.public_goods_game_environment = public_goods_game_environment
        self.history = history
        self.root = root

        self.root.title("Social Simulation")
        self.root.configure(bg='black')
        self.root.state('zoomed')

        self.setup_main_layout()
        self.enable_mouse_scroll()

    def enable_mouse_scroll(self):
        """Ermöglicht das Scrollen mit dem Mausrad."""
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)  # Windows und Linux
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)  # Mac Scroll Up
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)  # Mac Scroll Down

    def _on_mouse_wheel(self, event):
        """Behandelt das Scrollen mit dem Mausrad."""
        if event.num == 4 or event.delta > 0:  # Scroll Up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll Down
            self.canvas.yview_scroll(1, "units")

    def setup_main_layout(self):
        # Hauptlayout mit Scrollbar
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas mit Scrollbar für dynamisches Layout
        self.canvas = tk.Canvas(self.main_frame, bg='black')
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='black')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill=tk.Y)

    def update(self):
        # Erstelle ein verstecktes Frame für neue Inhalte
        buffer_frame = tk.Frame(self.canvas, bg='black')
        buffer_frame.pack(fill=tk.BOTH, expand=True)

        # Aktualisiere die neuen Daten in das Buffer-Frame
        history = self.history.get_history()
        for round_data in history:
            self.display_round_data(round_data, buffer_frame)

        # Ersetze das alte scrollable_frame durch das Buffer-Frame
        self.scrollable_frame.destroy()
        self.scrollable_frame = buffer_frame

        # Aktualisiere die Canvas-Ansicht
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def display_round_data(self, round_data, parent_frame):
        # Rahmen für die aktuelle Runde
        round_frame = tk.Frame(parent_frame, bg='gray20', pady=10, padx=10)
        round_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        # Label für die Rundenüberschrift
        round_label = tk.Label(
            round_frame,
            text=f"{round_data['label']}",
            fg="white",
            bg='gray20',
            font=("Helvetica", 20, "bold")
        )
        round_label.pack(anchor="w")

        # Vermögen der Agenten anzeigen
        fortunes_frame = tk.Frame(round_frame, bg='gray30', pady=5)
        fortunes_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            fortunes_frame,
            text="Vermögen der Agenten:",
            fg="white",
            bg='gray30',
            font=("Helvetica", 16)
        ).pack(anchor="w")

        for agent, fortune in round_data['fortunes'].items():
            tk.Label(
                fortunes_frame,
                text=f"{agent.name}, {agent.actr_agent_type_name}: {fortune}",
                fg="lightgray",
                bg='gray30',
                font=("Helvetica", 14)
            ).pack(anchor="w", padx=20)

        # Entscheidungen der Agenten
        decisions_frame = tk.Frame(round_frame, bg='gray30', pady=5)
        decisions_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            decisions_frame,
            text="Entscheidungen der Agenten:",
            fg="white",
            bg='gray30',
            font=("Helvetica", 16)
        ).pack(anchor="w")

        for agent, decision in round_data['agent_decisions'].items():
            agent_dict = agent.get_agent_dictionary()

            # Mögliche Entscheidungen
            options_text = "Mögliche Entscheidungen: "
            if isinstance(decision['options'], list):
                options_text += ", ".join(
                    f"{agent_dict[key]['agent'].name} (Status: {agent_dict[key]['social_status']}): {value}"
                    for option in decision['options']
                    for key, value in option.items() if key != 'id' and key in agent_dict
                )
            else:
                options_text += "Keine Daten verfügbar"

            # Gewählte Entscheidung
            selected_option_text = "Gewählte Entscheidung: "
            if isinstance(decision['selected_option'], tuple):
                # Extrahiere die beiden Teile der Haupt-Tuple
                selected_option_data, status_data = decision['selected_option']

                # Debug: Struktur des inneren Tupels
                print(f"DEBUG: selected_option_data: {selected_option_data}")
                print(f"DEBUG: status_data: {status_data}")

                # Verarbeite den inneren Tupel
                if isinstance(selected_option_data, tuple) and len(selected_option_data) == 2:
                    values, statuses = selected_option_data  # Entpacken der beiden Dictionaries
                    print(f"DEBUG: values: {values}")
                    print(f"DEBUG: statuses: {statuses}")

                    if isinstance(values, dict) and isinstance(statuses, dict):
                        selected_option_text += ", ".join(
                            f"{key}: {value} ({statuses.get(key, 'neutral')})"
                            for key, value in values.items() if key != 'id'
                        )
                    else:
                        selected_option_text += "Unerwartete Struktur in selected_option_data"
                else:
                    selected_option_text += "Unerwartete Struktur in selected_option_data"
            else:
                selected_option_text += "Keine"

            # Anzeige in der GUI
            tk.Label(
                decisions_frame,
                text=f"{agent.name}, {agent.actr_agent_type_name}",
                fg="lightgray",
                bg='gray30',
                font=("Helvetica", 14)
            ).pack(anchor="w", padx=20)

            tk.Label(
                decisions_frame,
                text=options_text,
                fg="lightgray",
                bg='gray30',
                font=("Helvetica", 12)
            ).pack(anchor="w", padx=40)

            tk.Label(
                decisions_frame,
                text=selected_option_text,
                fg="lightgray",
                bg='gray30',
                font=("Helvetica", 12)
            ).pack(anchor="w", padx=40)

        # Nominierungen
        nominations_frame = tk.Frame(round_frame, bg='gray30', pady=5)
        nominations_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            nominations_frame,
            text="Nominierungen (Belohnung/Bestrafung):",
            fg="white",
            bg='gray30',
            font=("Helvetica", 16)
        ).pack(anchor="w")

        for row in round_data['nominations']:
            tk.Label(
                nominations_frame,
                text=" ".join(row),
                fg="lightgray",
                bg='gray30',
                font=("Helvetica", 14)
            ).pack(anchor="w", padx=20)

        # Belohnte und bestrafte Agenten
        actions_frame = tk.Frame(round_frame, bg='gray30', pady=5)
        actions_frame.pack(fill=tk.X, padx=10)

        tk.Label(
            actions_frame,
            text="Belohnte Agenten:",
            fg="white",
            bg='gray30',
            font=("Helvetica", 16)
        ).pack(anchor="w")
        tk.Label(
            actions_frame,
            text=", ".join(agent.name for agent in round_data['rewarded']) or "-",
            fg="lightgray",
            bg='gray30',
            font=("Helvetica", 14)
        ).pack(anchor="w", padx=20)

        tk.Label(
            actions_frame,
            text="Bestrafte Agenten:",
            fg="white",
            bg='gray30',
            font=("Helvetica", 16)
        ).pack(anchor="w")
        tk.Label(
            actions_frame,
            text=", ".join(agent.name for agent in round_data['punished']) or "-",
            fg="lightgray",
            bg='gray30',
            font=("Helvetica", 14)
        ).pack(anchor="w", padx=20)
