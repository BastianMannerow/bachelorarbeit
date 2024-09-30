import environment.Middleman as middleman
import environment.Game as game
from agent.AgentTypeReturner import AgentTypeReturner
import environment.AgentConstruct as agent_builder
from environment.History import History

import pyactr as actr
import random
import tkinter as tk

class ClassicPublicGoodsGame:
    def __init__(self, focus_position):
        self.focus_position = focus_position
        self.agent_list = []
        self.root = tk.Tk()
        self.agent_type_returner = AgentTypeReturner()
        self.turn_count = 0  # To track the number of turns taken

        self.middleman = middleman.get_middleman(None, self)
        self.actr_environment = actr.Environment(focus_position=self.focus_position)
        self.experiment_environment = None

        self.manual_input_controller = None
        self.history = History()

        # Configuration
        self.agent_types = ["Human", "Test"]  # Needs to be the same name as the .py in the agent folder
        self.fortune_list = [5, 5]
        self.contribution_cost_factor_list = [1, 1]

        self.transparency = False
        self.reward = 0
        self.punishment = 0
        self.multiplication_factor = 2


    def agent_builder(self):
        with open("gui/iteration2/sprites/pokemon/pokemonNames.txt", 'r') as file:
            names = file.read().splitlines()
        original_names = names.copy()
        random.shuffle(names)
        for agent_type in self.agent_types:
            agent_model = self.agent_type_returner.return_agent_type(agent_type, self.actr_environment)
            name = names.pop()
            name_number = original_names.index(name) + 1
            agent = agent_builder.build_agent(agent_model, self.actr_environment, self.middleman, name, name_number)
            self.agent_list.append(agent)

            # Check if the agent_type is None, indicating a Human agent
            if agent.agent_type is None:
                self.manual_input_controller = ManualInputController(self.middleman, agent)

        for agent in self.agent_list:
            agent.set_agent_dictionary(self.agent_list)

    def run_simulation(self):
        # Initialise
        self.agent_builder()
        self.experiment_environment = game.get_environment(self.transparency, self.reward, self.punishment, self.multiplication_factor, self.agent_list, self.history, self.root)
        self.middleman.set_environment(self.experiment_environment)

        def move_step(count=0):
            if count < 20:
                self.execute_step(count)

        move_step()
        self.root.mainloop()  # Allows GUI to run even while waiting for events

    def execute_step(self, count):
        current_agent = self.agent_list[0]

        # If agent_type is None (Human), expect manual input
        if current_agent.agent_type is None:
            # Wait for manual input (for example, from the GUI or console)
            input_str = self.get_manual_input()
            self.manual_input_controller.handle_input(input_str)
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

    def next_turn(self):
        # Rotate the agent list to simulate the next agent's turn
        if self.agent_list:
            self.turn_count += 1
            self.agent_list = self.agent_list[1:] + [self.agent_list[0]]
            for agent in self.agent_list:
                agent.update_stimulus()

            # Check if all agents have taken their turn (one full round completed)
            if self.turn_count % len(self.agent_list) == 0:
                print("Round Completed")
                self.experiment_environment.round_completed()
                self.middleman.round_completed()
