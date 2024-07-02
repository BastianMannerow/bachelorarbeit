import environment.iteration2.LevelBuilder as levelbuilder
import environment.iteration2.Middleman as middleman
import environment.iteration2.MatrixWorld as matrix_world
import agents.iteration1.Autoclicker as autoclicker

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
        self.realtime = True

        self.focus_position = focus_position
        self.environment = actr.Environment(focus_position=(100, 100))
        self.active_agent_simulation = []
        self.active_agent_name = []
        self.root = tk.Tk()

    def agent_builder(self):
        initial_triggers = ['X', 'Y', 'Z']
        initial_text_stimuli = [
            {'X': {'text': 'X', 'position': (100, 100)}},
            {'Y': {'text': 'Y', 'position': (200, 200)}},
            {'Z': {'text': 'Z', 'position': (300, 300)}}
        ]

        with open("environment/iteration2/first-names.txt", 'r') as file:
            names = file.read().splitlines()

        for _ in range(self.agent_amount):
            agent = autoclicker.get_agent(self.environment, self.middleman, "A")
            agent_simulation = agent.simulation(realtime=self.realtime,
                                                environment_process=self.environment.environment_process,
                                                stimuli=initial_text_stimuli,
                                                triggers=initial_triggers,
                                                times=1)
            self.active_agent_simulation.append(agent_simulation)
            self.active_agent_name.append(random.choice(names))

    def run_simulation(self):
        # Initialise
        self.agent_builder()
        level_matrix = levelbuilder.build_level(self.height, self.width, self.active_agent_simulation, self.food_amount,
                                                self.wall_density)
        environment = matrix_world.get_environment(level_matrix, self.root)
        self.middleman.set_environment(environment)

        def move_step(count=0):
            if count < 20:
                self.execute_step(count)

        move_step()
        self.root.mainloop()  # Allows GUI to run even while waiting for events

    def execute_step(self, count):
        self.active_agent_simulation[0].step()
        print(f"{self.active_agent_name[0]}, {self.active_agent_simulation[0].current_event}")
        event = self.active_agent_simulation[0].current_event

        if event[1] == "manual" and "KEY PRESSED:" in event[2]:
            self.middleman.motor_input_to_environment(event[2], self.active_agent_simulation[0])
            self.next_turn()
            # Wait before the next agent may do its move
            self.root.after(1000, lambda: self.execute_step(count + 1))
        else:
            self.root.after_idle(lambda: self.execute_step(count + 1))

    def next_turn(self):
        if self.active_agent_simulation:
            self.active_agent_simulation = self.active_agent_simulation[1:] + [self.active_agent_simulation[0]]

        if self.active_agent_name:
            self.active_agent_name = self.active_agent_name[1:] + [self.active_agent_name[0]]


    def change_stimulus(self):
        new_triggers = ['X', 'Y', 'Z']
        new_text = [
            {'X': {'text': 'X', 'position': (100, 100)}},
            {'Y': {'text': 'Y', 'position': (200, 200)}},
            {'Z': {'text': 'Z', 'position': (300, 300)}}
        ]

        print("----------------------------------")
        print(f"{self.active_agent_simulation[0]._Simulation__env.triggers}")
        print(f"{self.active_agent_simulation[0]._Simulation__env.stimuli}")
        print("----------------------------------")
        self.active_agent_simulation[0]._Simulation__env.triggers = new_triggers
        self.active_agent_simulation[0]._Simulation__env.stimuli = new_text
        print("----------------------------------")
        print(f"{self.active_agent_simulation[0]._Simulation__env.triggers}")
        print(f"{self.active_agent_simulation[0]._Simulation__env.stimuli}")
        print("----------------------------------")