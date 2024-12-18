import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class PublicGoodsGameGUI:
    def __init__(self, simulation, public_goods_game_environment, history, root):
        self.simulation = simulation
        self.public_goods_game_environment = public_goods_game_environment
        self.history = history
        self.root = root

        self.root.title("Social Simulation")
        self.root.configure(bg='black')
        self.root.state('zoomed')

        self.agent_data = {}  # Speichert Daten für den Plot

        self.setup_main_layout()
        self.enable_mouse_scroll()
        self.setup_plot()

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

    def setup_plot(self):
        """Erstellt den Plotbereich auf der rechten Seite."""
        self.plot_frame = tk.Frame(self.root, bg='black')
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        # Erstellen der Matplotlib-Figur
        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        # Einbetten in die Tkinter-Oberfläche
        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self, round_data):
        """Aktualisiert den Plot mit neuen Runden-Daten."""
        if round_data['label'] == 'Runde 0':
            return  # Plot in Runde 0 nicht zeichnen

        for agent, decision in round_data['agent_decisions'].items():
            own_contribution = decision['selected_option']['id']

            # Berechne den Durchschnitt der anderen Gruppenmitglieder
            other_contributions = [
                other_decision['selected_option']['id']
                for other_agent, other_decision in round_data['agent_decisions'].items()
                if other_agent != agent
            ]
            avg_contribution = sum(other_contributions) / len(other_contributions) if other_contributions else 0

            # Speichere die Daten für den Agenten
            if agent not in self.agent_data:
                self.agent_data[agent] = {'x': [], 'y': []}
            self.agent_data[agent]['x'].append(avg_contribution)
            self.agent_data[agent]['y'].append(own_contribution)

        # Lösche den alten Plot und zeichne die neuen Daten
        self.ax.clear()
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        for agent, data in self.agent_data.items():
            self.ax.plot(data['x'], data['y'], label=f"{agent.name}")

        self.ax.legend()
        self.figure.tight_layout()
        self.canvas_plot.draw()

    def update(self):
        # Erstelle ein verstecktes Frame für neue Inhalte
        buffer_frame = tk.Frame(self.canvas, bg='black')
        buffer_frame.pack(fill=tk.BOTH, expand=True)

        # Aktualisiere die neuen Daten in das Buffer-Frame
        history = self.history.get_history()
        for round_data in history:
            self.display_round_data(round_data, buffer_frame)
            self.update_plot(round_data)  # Aktualisiere den Plot für jede Runde

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
            if isinstance(decision['selected_option'], dict):
                # Extrahiere die ID
                option_id = decision['selected_option'].get('id', 'Unbekannt')
                # Restliche Schlüssel-Werte-Paare anzeigen
                remaining_values = ", ".join(
                    f"{key}: {value}"
                    for key, value in decision['selected_option'].items() if key != 'id'
                )
                selected_option_text += f"ID {option_id}, {remaining_values}"
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
