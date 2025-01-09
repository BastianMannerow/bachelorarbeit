import csv
import tkinter as tk
import random
import os

import numpy as np
import simpy

from iteration2.environment.Game import Game
from iteration2.environment.Middleman import Middleman
from iteration2.controller.ManualInputController import ManualInputController
from iteration2.environment.AgentConstruct import AgentConstruct
from iteration2.agent.AgentTypeReturner import AgentTypeReturner
from iteration2.environment.History import History
import pyactr as actr


class ClassicPublicGoodsGame:
    def __init__(self, focus_position, end_after_rounds, experiment_name):
        self.experiment_name = experiment_name
        # Configuration
        self.print_agent_actions = False
        self.print_actr_construct_trace = False
        self.print_trace = False
        self.print_middleman = False
        self.fortune_list = [5, 5]
        self.contribution_cost_factor_list = [1, 1]

        self.start_fortune = 5
        self.population_size = 4
        self.contribution_limit = 20
        self.latency_factor_agent_actions = 1 # in ms
        self.reward = 0
        self.punishment = -2
        self.allow_punishment = True
        self.multiplication_factor = 1.4

        self.button_dictionary = {
            "R": "Reward",
            "P": "Punish",
            "S": "Strategie",
            "ENTER": "Bestätigen"
        }

        # Critical
        self.end_after_rounds = end_after_rounds
        self.focus_position = focus_position
        self.agent_list = []
        self.root = tk.Tk()
        self.agent_type_returner = AgentTypeReturner()
        self.turn_count = 0  # To track the number of turns taken

        self.middleman = Middleman(None, self, self.print_middleman, 0)
        self.actr_environment = actr.Environment(focus_position=self.focus_position)
        self.experiment_environment = None

        self.manual_input_controller = None
        self.history = History()

        self.submit_waiting = tk.BooleanVar(value=False)  # BooleanVar for waiting on submit

    # Creates agent objects, which will participate in the simulation.
    def agent_builder(self):
        current_path = os.getcwd()
        file_path = current_path + os.sep + "iteration2" + os.sep + "gui" + os.sep + "first-names.txt"
        with open(file_path, "r", encoding="utf-8") as file:
            names = [line.strip() for line in file if line.strip()]

        original_names = names.copy()
        random.shuffle(names)

        # Generate normally distributed values between 0.0 and 1.0
        social_agreeableness_values = np.random.normal(loc=0.5, scale=0.15, size=self.population_size)
        # Scale values within [0.0, 1.0]
        social_agreeableness_values = np.clip(social_agreeableness_values, 0.0, 1.0)

        agent_type = "SocialAgent"
        fortune = 5

        for i in range(self.population_size):
            name = names.pop()
            name_number = original_names.index(name) + 1
            social_agreeableness = social_agreeableness_values[i]
            agent = AgentConstruct(agent_type, self.actr_environment, self.middleman, name, name_number, fortune,
                                   social_agreeableness, 1, self.print_trace, self.print_actr_construct_trace)
            self.agent_list.append(agent)

            # Check if the agent_type is None, indicating a Human agent
            if agent.actr_agent is None:
                self.manual_input_controller = ManualInputController(self.middleman)

        for agent in self.agent_list:
            agent.set_agent_dictionary(self.agent_list)
            actr_construct = self.agent_type_returner.return_agent_type(agent.actr_agent_type_name, self.actr_environment, self.punishment)
            actr_agent = actr_construct.get_agent(list(agent.get_agent_dictionary().keys()), self.button_dictionary)
            agent.set_actr_construct(actr_construct)
            agent.set_actr_agent(actr_agent)
            agent.set_simulation()

    # Core Loop for the simulation
    def run_simulation(self):
        # Initialise
        self.agent_builder()
        self.experiment_environment = Game(self.reward, self.punishment, self.multiplication_factor,
                                           self.history, self, self.root)
        self.middleman.set_environment(self.experiment_environment)

        # Initialisiere Runde 0
        self.initialize_round_0()

        def move_step(count=0):
            if count < 20:
                self.execute_step(count)

        move_step()
        self.root.mainloop()  # Allows GUI to run even while waiting for events

    # Inside the loop. Handles Human/ACT-R events and is responsible for time delays between agents actions,
    def execute_step(self, count):
        current_agent = self.agent_list[0]

        # If agent_type is None (Human), expect manual input
        if current_agent.actr_agent is None:
            # Wait for input inside the GUI (Submit)
            self.submit_waiting.set(False)  # Reset submit waiting flag
            self.root.wait_variable(self.submit_waiting)  # Wait until submit button is pressed
            self.root.after(1000, lambda: self.execute_step(count + 1))

        # If agent_type is not None (ACT-R), expect a KEY PRESSED event.
        else:
            try:
                current_agent.simulation.step()
                if(self.print_agent_actions):
                    print(f"{current_agent.name}, {current_agent.simulation.current_event}")
                event = current_agent.simulation.current_event

                # The agent decided to press a key, which will be executed by the middleman. TODO
                if event[1] == "manual" and "KEY PRESSED:" in event[2]:
                    self.middleman.motor_input(event[2], current_agent)
                    self.root.after(1000, lambda: self.execute_step(count + 1))

                # The agent might be in a specific mental state, which requires Python intervention to override ACT-R.
                else:
                    current_agent.actr_extension()
                    self.root.after(self.latency_factor_agent_actions, lambda: self.execute_step(count + 1))

            # Error handling due to a crashed ACT-R agent, to rescue the simulation.
            except simpy.core.EmptySchedule:
                current_agent.handle_empty_schedule()
                self.root.after_idle(lambda: self.execute_step(count + 1))

    # Handles both: next turn and triggers events, if a full round was finished.
    def next_turn(self):
        if self.agent_list:
            self.turn_count += 1
            self.agent_list = self.agent_list[1:] + [self.agent_list[0]]
            for agent in self.agent_list:
                agent.update_stimulus()

            self.experiment_environment.gui.update()

            # Check if all agents have taken their turn (one full round completed
            if self.turn_count % len(self.agent_list) == 0:
                print("Round Completed")
                self.experiment_environment.round_completed()
                self.middleman.round_completed()
                self.history.start_new_round(round_number=0, initial_round=True)

                # Finish the experiment
                if self.history.round_counter > self.end_after_rounds:
                    self.save_experiment_data()


            print(f"|--------------------- {self.agent_list[0].name} ---------------------|")

    # Initialises the initial round, which is important, so that the agents will receive 0 instead of None information.
    def initialize_round_0(self):
        # Starte Runde 0 in der History
        self.history.start_new_round(0)

        # Initialisiere die Agentendaten für Runde 0
        for agent in self.agent_list:
            # Initialisiere das Vermögen des Agenten
            self.history.round_history[-1]['fortunes'][agent] = agent.get_fortune()

            # Initialisiere die Entscheidungen des Agenten
            self.history.round_history[-1]['agent_decisions'][agent] = {
                'options': {**{other_agent: 0 for other_agent in self.agent_list}, 'id': 0},
                'selected_option': {**{other_agent: 0 for other_agent in self.agent_list}, 'id': 0}
            }

            # Initialisiere kognitive Informationen (leer)
            self.history.round_history[-1]['agent_cognition'][agent] = {}

        # Initialisiere die Nominierungsmatrix
        num_agents = len(self.agent_list)
        nomination_matrix = [['-' for _ in range(num_agents)] for _ in range(num_agents)]
        self.history.round_history[-1]['nominations'] = nomination_matrix

        # Aktualisiere die GUI für Runde 0
        self.experiment_environment.gui.update()

        # Starte die nächste Runde (initialisiert mit Label "Runde0")
        self.history.start_new_round(round_number=0, initial_round=True)

        for agent in self.agent_list:
            agent.reset_simulation()

    # Triggers the gui to refresh
    def notify_gui(self):
        if hasattr(self, 'gui'):
            self.gui.update()

    # Saves the data as csv data format
    def save_experiment_data(self):
        history = self.history.get_history()

        # Saving Agent information
        for agent in self.agent_list:
            # Define CSV file name based on agent properties
            filename = f"{self.experiment_name}-{agent.name}-{agent.social_agreeableness}.csv"

            # Prepare data rows for the CSV file
            rows = []
            for round_data in history:
                label = round_data['label']
                fortune = round_data['fortunes'].get(agent, "")

                # Get contribution
                contribution = round_data.get("agent_decisions", {}).get(agent, {}).get("selected_option", {}).get("id",
                                                                                                                   "")

                # Determine if the agent was punished from the nomination matrix
                nominations = round_data.get("nominations", [])
                agent_index = self.agent_list.index(agent)
                punished = any(
                    nominations[agent_index][i] != '-' for i in range(len(self.agent_list))) if nominations else False

                # Get cognitive distortion and cognitive algebra
                cognition = round_data.get("agent_cognition", {}).get(agent, {})

                cognitive_distortions = []
                cognitive_algebras = []

                for target_agent, cognition_data in cognition.items():
                    cognitive_distortions.append(
                        f"{target_agent.name}: {cognition_data.get('cognitive_distortion', '')}")
                    cognitive_algebras.append(f"{target_agent.name}: {cognition_data.get('cognitive_algebra', '')}")

                cognitive_distortion = " | ".join(cognitive_distortions)
                cognitive_algebra = " | ".join(cognitive_algebras)

                # Add row for each round
                rows.append([label, fortune, contribution, punished, cognitive_distortion, cognitive_algebra])

            # Write data to CSV
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(
                    ["Runde", "Fortune", "Contribution", "Punished", "Cognitive Distortion", "Cognitive Algebra"])
                # Write rows
                writer.writerows(rows)

        # Saving Configuration information
        filename = f"{self.experiment_name}-configuration.csv"
        main_data = {
            "population_size": len(self.agent_list),
            "multiplication_factor": self.multiplication_factor,
            "contribution_limit": self.contribution_limit,
            "punishment": self.punishment,
            "start_fortune": self.start_fortune,
        }

        # Daten für die Agenten sammeln
        agent_data = [{"agent": agent, "agent_name": agent.name} for agent in self.agent_list]

        # CSV schreiben
        with open(filename, mode="w", newline="") as file:
            # Alle Spalten zusammenstellen
            fieldnames = list(main_data.keys()) + ["agent", "agent_name"]

            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            # Hauptdaten einfügen (nur einmal, Werte auf alle Felder verteilen)
            main_row = {**main_data, **{"agent": "", "agent_name": ""}}
            writer.writerow(main_row)

            # Agentendaten einfügen
            for agent_row in agent_data:
                writer.writerow({**{key: "" for key in main_data.keys()}, **agent_row})

        # Quit the root GUI loop
        self.root.quit()
