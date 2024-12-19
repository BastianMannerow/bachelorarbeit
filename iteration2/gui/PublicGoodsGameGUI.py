import tkinter as tk
from tkinter import ttk

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

        self.agent_data = {}
        self.contribution_data = {}
        self.fortune_data = {}

        self.current_round_index = 0

        self.setup_main_layout()
        self.enable_mouse_scroll()

        # Korrekte Aufrufe der Plot-Methoden
        self.setup_plot()  # Erster Plot
        self.setup_middle_plot()  # Zweiter Plot
        self.setup_left_plot()  # Dritter Plot

        self.setup_left_area()
        self.setup_round_selector()

    def enable_mouse_scroll(self):
        # Binde das Scrollen an das richtige Frame
        self.left_frame.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.left_frame.bind_all("<Button-4>", self._on_mouse_wheel)
        self.left_frame.bind_all("<Button-5>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def setup_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg='black')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Linker Bereich
        self.left_frame = tk.Frame(self.main_frame, bg='black', width=500)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Rechter Bereich (für drei Plots untereinander)
        self.right_frame = tk.Frame(self.main_frame, bg='black', width=500)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

    def setup_left_area(self):
        # Canvas und Scrollbar für den linken Bereich
        self.canvas = tk.Canvas(self.left_frame, bg='gray20')
        self.scrollbar = tk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='gray20')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side="right", fill=tk.Y)

        # Setze `info_frame` als scrollbaren Bereich
        self.info_frame = tk.Frame(self.scrollable_frame, bg='gray20', pady=10, padx=10)
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        self.update_left_area()

    def setup_round_selector(self):
        # Bereich für das Dropdown-Menü zur Rundenauswahl
        self.round_selector_frame = tk.Frame(self.left_frame, bg='gray30')
        self.round_selector_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Label für das Dropdown-Menü
        tk.Label(
            self.round_selector_frame,
            text="Runde auswählen:",
            fg="white",
            bg='gray30',
            font=("Helvetica", 14)
        ).pack(side=tk.LEFT, padx=10)

        # Dropdown-Menü
        self.round_selector = ttk.Combobox(
            self.round_selector_frame,
            values=[f"Runde {i}" for i in range(len(self.history.get_history()))],
            state="readonly",
            font=("Helvetica", 14)
        )
        self.round_selector.pack(side=tk.LEFT, padx=10)
        self.round_selector.bind("<<ComboboxSelected>>", self.change_round)

    def update_left_area(self):
        # Entferne vorherige Widgets im linken Bereich
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Überprüfe, ob die Historie leer ist
        history = self.history.get_history()
        if not history:
            tk.Label(
                self.info_frame,
                text="Keine Daten verfügbar",
                fg="white",
                bg="gray20",
                font=("Helvetica", 16)
            ).pack(anchor="center")
            return

        # Zeige die aktuelle Runde an
        round_data = history[self.current_round_index]
        self.display_round_data(round_data, self.info_frame)

    def change_round(self, event):
        # Rundenindex basierend auf der Auswahl aktualisieren
        selected_round = self.round_selector.get()
        match = re.search(r'Runde (\d+)', selected_round)
        if match:
            self.current_round_index = int(match.group(1))
            self.update_left_area()  # Aktualisiere die linke Ansicht

    def setup_plot(self):
        # Berechne die Höhe für den Plot basierend auf der Bildschirmhöhe
        screen_height = self.root.winfo_screenheight()
        plot_height = screen_height // 3

        # Frame für den ersten Plot
        self.plot_frame = tk.Frame(self.right_frame, bg='black', height=plot_height)
        self.plot_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Erster Plot (Agent Contributions) mit fester Größe
        self.figure = plt.figure(figsize=(5, plot_height / 100), dpi=100)  # Dynamische Höhe
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        self.canvas_plot = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_middle_plot(self):
        # Berechne die Höhe für den Plot basierend auf der Bildschirmhöhe
        screen_height = self.root.winfo_screenheight()
        plot_height = screen_height // 3

        # Frame für den zweiten Plot
        self.middle_plot_frame = tk.Frame(self.right_frame, bg='black', height=plot_height)
        self.middle_plot_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Zweiter Plot (Fortune Over Time) mit fester Größe
        self.middle_figure = plt.figure(figsize=(5, plot_height / 100), dpi=100)  # Dynamische Höhe
        self.middle_ax = self.middle_figure.add_subplot(111)
        self.middle_ax.set_title("Fortune Over Time")
        self.middle_ax.set_xlabel("Time")
        self.middle_ax.set_ylabel("Fortune")

        self.middle_canvas_plot = FigureCanvasTkAgg(self.middle_figure, master=self.middle_plot_frame)
        self.middle_canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def setup_left_plot(self):
        # Berechne die Höhe für den Plot basierend auf der Bildschirmhöhe
        screen_height = self.root.winfo_screenheight()
        plot_height = screen_height // 3

        # Frame für den dritten Plot
        self.left_plot_frame = tk.Frame(self.right_frame, bg='black', height=plot_height)
        self.left_plot_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Dritter Plot (Rundenverlauf der Contributions) mit fester Größe
        self.left_figure = plt.figure(figsize=(5, plot_height / 100), dpi=100)  # Dynamische Höhe
        self.left_ax = self.left_figure.add_subplot(111)
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

        # Zeichne den Plot neu ohne Legende
        self.ax.clear()
        self.ax.set_title("Agent Contributions")
        self.ax.set_xlabel("Average Contribution of Others")
        self.ax.set_ylabel("Own Contribution")

        for agent, data in self.agent_data.items():
            sorted_data = sorted(zip(data['x'], data['y']), key=lambda pair: pair[0])
            x_sorted, y_sorted = zip(*sorted_data)
            self.ax.plot(x_sorted, y_sorted)  # Entferne das `label`-Argument

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

        # Zeichne den Plot neu ohne Legende
        self.middle_ax.clear()
        self.middle_ax.set_title("Fortune Over Time")
        self.middle_ax.set_xlabel("Time")
        self.middle_ax.set_ylabel("Fortune")

        for agent, data in self.fortune_data.items():
            sorted_data = sorted(zip(data['rounds'], data['fortunes']), key=lambda pair: pair[0])
            rounds_sorted, fortunes_sorted = zip(*sorted_data)
            self.middle_ax.plot(rounds_sorted, fortunes_sorted)  # Entferne das `label`-Argument

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

        # Zeichne den Plot neu ohne Legende
        self.left_ax.clear()
        self.left_ax.set_title("Rundenverlauf der Contributions")
        self.left_ax.set_xlabel("Runden")
        self.left_ax.set_ylabel("Contribution")

        for agent, data in self.contribution_data.items():
            sorted_data = sorted(zip(data['rounds'], data['contributions']), key=lambda pair: pair[0])
            rounds_sorted, contributions_sorted = zip(*sorted_data)
            self.left_ax.plot(rounds_sorted, contributions_sorted)  # Entferne das `label`-Argument

        self.left_figure.tight_layout()
        self.left_canvas_plot.draw()

    def update(self):
        self.update_left_area()  # Links die aktuelle Runde aktualisieren
        for round_data in self.history.get_history():
            self.update_plot(round_data)
            self.update_middle_plot(round_data)
            self.update_left_plot(round_data)

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
