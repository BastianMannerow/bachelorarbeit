import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import re

class PublicGoodsGameGUI:
    def __init__(self, simulation, public_goods_game_environment, history, root):
        self.simulation = simulation
        self.public_goods_game_environment = public_goods_game_environment
        self.history = history
        self.root = root

        self.root.title("Social Simulation")
        self.root.configure(bg='black')
        self.root.state('zoomed')

        self.agent_data = {}  # Speichert Daten für den rechten Plot
        self.contribution_data = {}  # Speichert Daten für den linken Plot
        self.fortune_data = {}  # Speichert Daten für den mittleren Plot

        self.setup_main_layout()
        self.enable_mouse_scroll()
        self.setup_plot()
        self.setup_middle_plot()
        self.setup_left_plot()

    def enable_mouse_scroll(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind_all("<Button-5>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def setup_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

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
        self.plot_frame = tk.Frame(self.root, bg='black')
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)

        self.figure, self.ax = plt.subplots()
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_middle_plot(self):
        self.middle_plot_frame = tk.Frame(self.root, bg='black')
        self.middle_plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.middle_figure, self.middle_ax = plt.subplots()
        self.middle_ax.set_title("Fortune Over Time")
        self.middle_ax.set_xlabel("Time")
        self.middle_ax.set_ylabel("Fortune")

        self.middle_canvas_plot = FigureCanvasTkAgg(self.middle_figure, master=self.middle_plot_frame)
        self.middle_canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_left_plot(self):
        self.left_plot_frame = tk.Frame(self.root, bg='black')
        self.left_plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.left_figure, self.left_ax = plt.subplots()
        self.left_ax.set_title("Rundenverlauf der Contributions")
        self.left_ax.set_xlabel("Runden")
        self.left_ax.set_ylabel("Contribution")

        self.left_canvas_plot = FigureCanvasTkAgg(self.left_figure, master=self.left_plot_frame)
        self.left_canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot(self, round_data):
        if round_data['label'] == 'Runde 0':
            return

        for agent, decision in round_data['agent_decisions'].items():
            own_contribution = decision['selected_option']['id']
            other_contributions = [
                other_decision['selected_option']['id']
                for other_agent, other_decision in round_data['agent_decisions'].items()
                if other_agent != agent
            ]
            avg_contribution = sum(other_contributions) / len(other_contributions) if other_contributions else 0

            if agent not in self.agent_data:
                self.agent_data[agent] = {'x': [], 'y': []}
            self.agent_data[agent]['x'].append(avg_contribution)
            self.agent_data[agent]['y'].append(own_contribution)

        self.ax.clear()
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        for agent, data in self.agent_data.items():
            sorted_data = sorted(zip(data['x'], data['y']), key=lambda pair: pair[0])
            x_sorted, y_sorted = zip(*sorted_data)
            self.ax.plot(x_sorted, y_sorted, label=f"{agent.name}")

        self.ax.legend()
        self.figure.tight_layout()
        self.canvas_plot.draw()

    def update_middle_plot(self, round_data):
        round_number = None
        if 'Runde' in round_data['label']:
            match = re.search(r'Runde(\d+)', round_data['label'])
            if match:
                round_number = int(match.group(1))

        for agent, fortune in round_data['fortunes'].items():
            if agent not in self.fortune_data:
                self.fortune_data[agent] = {'rounds': [], 'fortunes': []}
            self.fortune_data[agent]['rounds'].append(round_number)
            self.fortune_data[agent]['fortunes'].append(fortune)

        self.middle_ax.clear()
        self.middle_ax.set_title("Fortune Over Time")
        self.middle_ax.set_xlabel("Time")
        self.middle_ax.set_ylabel("Fortune")

        for agent, data in self.fortune_data.items():
            sorted_data = sorted(zip(data['rounds'], data['fortunes']), key=lambda pair: pair[0])
            rounds_sorted, fortunes_sorted = zip(*sorted_data)
            self.middle_ax.plot(rounds_sorted, fortunes_sorted, label=f"{agent.name}")

        self.middle_ax.legend()
        self.middle_figure.tight_layout()
        self.middle_canvas_plot.draw()

    def update_left_plot(self, round_data):
        round_number = None
        if 'Runde' in round_data['label']:
            match = re.search(r'Runde(\d+)', round_data['label'])
            if match:
                round_number = int(match.group(1))

        for agent, decision in round_data['agent_decisions'].items():
            contribution = decision['selected_option']['id']

            if agent not in self.contribution_data:
                self.contribution_data[agent] = {'rounds': [], 'contributions': []}
            self.contribution_data[agent]['rounds'].append(round_number)
            self.contribution_data[agent]['contributions'].append(contribution)

        self.left_ax.clear()
        self.left_ax.set_title("Rundenverlauf der Contributions")
        self.left_ax.set_xlabel("Runden")
        self.left_ax.set_ylabel("Contribution")

        for agent, data in self.contribution_data.items():
            # Sortiere Daten nach Runden
            sorted_data = sorted(zip(data['rounds'], data['contributions']), key=lambda pair: pair[0])
            rounds_sorted, contributions_sorted = zip(*sorted_data)
            self.left_ax.plot(rounds_sorted, contributions_sorted, label=f"{agent.name}")

        self.left_ax.legend()
        self.left_figure.tight_layout()
        self.left_canvas_plot.draw()

    def update(self):
        buffer_frame = tk.Frame(self.canvas, bg='black')
        buffer_frame.pack(fill=tk.BOTH, expand=True)

        history = self.history.get_history()
        for round_data in history:
            self.display_round_data(round_data, buffer_frame)
            self.update_plot(round_data)
            self.update_middle_plot(round_data)
            self.update_left_plot(round_data)

        self.scrollable_frame.destroy()
        self.scrollable_frame = buffer_frame

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
