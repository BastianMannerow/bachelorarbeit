import tkinter as tk
import random
from environment.Game import Game
from environment.Middleman import Middleman
from controller.ManualInputController import ManualInputController
from environment.AgentConstruct import AgentConstruct
from agent.AgentTypeReturner import AgentTypeReturner
from environment.History import History
import pyactr as actr


class ClassicPublicGoodsGame:
    def __init__(self, focus_position):
        self.focus_position = focus_position
        self.agent_list = []
        self.root = tk.Tk()
        self.agent_type_returner = AgentTypeReturner()
        self.turn_count = 0  # To track the number of turns taken

        self.middleman = Middleman(None, self)
        self.actr_environment = actr.Environment(focus_position=self.focus_position)
        self.experiment_environment = None

        self.manual_input_controller = None
        self.history = History()

        self.submit_waiting = tk.BooleanVar(value=False)  # BooleanVar for waiting on submit

        # Configuration
        self.agent_types = ["Human", "Human", "Human"]
        self.fortune_list = [5, 5]
        self.contribution_cost_factor_list = [1, 1]

        self.reward = 0
        self.punishment = 0
        self.multiplication_factor = 2

    def agent_builder(self):
        names = ["Basti", "Niki", "Frank", "Ulrike", "Louisa", "Lara"]
        original_names = names.copy()
        random.shuffle(names)
        for agent_type in self.agent_types:
            agent_model = self.agent_type_returner.return_agent_type(agent_type, self.actr_environment)
            name = names.pop()
            name_number = original_names.index(name) + 1
            agent = AgentConstruct(agent_model, self.actr_environment, self.middleman, name, name_number, 10, 1)
            self.agent_list.append(agent)

            # Check if the agent_type is None, indicating a Human agent
            if agent.actr_agent is None:
                self.manual_input_controller = ManualInputController(self.middleman)

        for agent in self.agent_list:
            agent.set_agent_dictionary(self.agent_list)

    def run_simulation(self):
        # Initialise
        self.agent_builder()
        self.experiment_environment = Game(self.reward, self.punishment, self.multiplication_factor,
                                           self.history, self, self.root)
        self.middleman.set_environment(self.experiment_environment)

        def move_step(count=0):
            if count < 20:
                self.execute_step(count)

        move_step()
        self.root.mainloop()  # Allows GUI to run even while waiting for events

    def execute_step(self, count):
        current_agent = self.agent_list[0]

        # If agent_type is None (Human), expect manual input
        if current_agent.actr_agent is None:
            # Warte auf Eingabe durch GUI (Submit)
            self.submit_waiting.set(False)  # Reset submit waiting flag
            self.root.wait_variable(self.submit_waiting)  # Wait until submit button is pressed
            self.root.after(1000, lambda: self.execute_step(count + 1))
        else:
            # Simulate the step for non-human agents
            current_agent.simulation.step()
            print(f"{current_agent.name}, {current_agent.simulation.current_event}")
            event = current_agent.simulation.current_event
            if event[1] == "manual" and "KEY PRESSED:" in event[2]:
                self.middleman.motor_input_to_environment(event[2], current_agent)
                self.root.after(1000, lambda: self.execute_step(count + 1))
            else:
                self.root.after_idle(lambda: self.execute_step(count + 1))

    def notify_gui(self):
        if hasattr(self, 'gui'):
            self.gui.update()  # Die GUI entscheidet, was aktualisiert wird

    def next_turn(self):
        if self.agent_list:
            self.turn_count += 1
            self.agent_list = self.agent_list[1:] + [self.agent_list[0]]
            for agent in self.agent_list:
                agent.update_stimulus()

            self.experiment_environment.gui.update()

            # Check if all agents have taken their turn (one full round completed)
            if self.turn_count % len(self.agent_list) == 0:
                print("Round Completed")
                self.experiment_environment.round_completed()
                self.middleman.round_completed()

