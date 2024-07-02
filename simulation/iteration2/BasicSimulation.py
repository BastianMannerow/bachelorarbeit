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
        text_stimuli = None
        triggers = None

        with open("environment/iteration2/first-names.txt", 'r') as file:
            names = file.read().splitlines()

        for _ in range(self.agent_amount):
            agent = autoclicker.get_agent(self.environment, self.middleman, "A")
            agent_simulation = agent.simulation(realtime=self.realtime,
                                                environment_process=self.environment.environment_process,
                                                stimuli=text_stimuli,
                                                triggers=triggers,
                                                times=1)
            self.active_agent_simulation.append(agent_simulation)
            self.active_agent_name.append(random.choice(names))

    def run_simulation(self):
        # initialise
        self.agent_builder()
        level_matrix = levelbuilder.build_level(self.height, self.width, self.active_agent_simulation, self.food_amount,
                                                self.wall_density)
        environment = matrix_world.get_environment(level_matrix, self.root)  # Pass the root to MatrixWorld
        self.middleman.set_environment(environment)

        def move():
            count = 0
            def move_step():
                nonlocal count
                if count < 20:
                    environment.move_agent_right(self.active_agent_simulation[0])
                    count += 1
                    self.root.after(1000, move_step)  # Wait for 1 second and call move_step again
            move_step()

        move()
        self.root.mainloop()  # Start the GUI event loop

    def next_turn(self):
        if self.active_agent_simulation:
            self.active_agent_simulation = self.active_agent_simulation[1:] + [self.active_agent_simulation[0]]

        if self.active_agent_name:
            self.active_agent_name = self.active_agent_name[1:] + [self.active_agent_name[0]]

    def execute_step(self):
        self.active_agent_simulation[0].step()
        print(f"{self.active_agent_name[0]}, {self.active_agent_simulation[0].current_event}")
        event = self.active_agent_simulation[0].current_event

        if event[1] == "manual" and "KEY PRESSED:" in event[2]:
            self.middleman.motor_input_to_environment(event[2])
            self.next_turn()
            self.change_stimulus()

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