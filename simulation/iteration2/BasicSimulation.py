import environment.iteration2.LevelBuilder as levelbuilder
import environment.iteration2.Middleman as middleman
import environment.iteration2.MatrixWorld as matrix_world
import agents.iteration1.Autoclicker as autoclicker
import agents.iteration2.Agent as agent_builder

import pyactr as actr
import random
import tkinter as tk

class BasicSimulation:
    def __init__(self, focus_position):
        self.width = 10
        self.height = 10
        self.food_amount = 4
        self.wall_density = 10
        self.agent_amount = 2

        self.middleman = middleman.get_middleman(None)
        self.environment = actr.Environment(focus_position=(100, 100))

        self.focus_position = focus_position
        self.agent_list = []
        self.root = tk.Tk()

    def agent_builder(self):
        with open("environment/iteration2/first-names.txt", 'r') as file:
            names = file.read().splitlines()

        for _ in range(self.agent_amount):
            agent_type = autoclicker.get_agent(self.environment, self.middleman, "A")
            agent = agent_builder.build_agent(agent_type, self.environment, random.choice(names))
            self.agent_list.append(agent)

    def run_simulation(self):
        # Initialise
        self.agent_builder()
        level_matrix = levelbuilder.build_level(self.height, self.width, self.agent_list, self.food_amount,
                                                self.wall_density)
        environment = matrix_world.get_environment(level_matrix, self.root)
        self.middleman.set_environment(environment)

        def move_step(count=0):
            if count < 20:
                self.execute_step(count)

        move_step()
        self.root.mainloop()  # Allows GUI to run even while waiting for events

    def execute_step(self, count):
        self.agent_list[0].simulation.step()
        print(f"{self.agent_list[0].name}, {self.agent_list[0].simulation.current_event}")
        event = self.agent_list[0].simulation.current_event

        if event[1] == "manual" and "KEY PRESSED:" in event[2]:
            self.middleman.motor_input_to_environment(event[2], self.agent_list[0])
            self.next_turn()
            # Wait before the next agent may do its move
            self.root.after(1000, lambda: self.execute_step(count + 1))
        else:
            self.root.after_idle(lambda: self.execute_step(count + 1))

    def next_turn(self):
        if self.agent_list:
            self.agent_list = self.agent_list[1:] + [self.agent_list[0]]
            # TODO changing visual stimuli

