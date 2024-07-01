from agents.iteration1 import Autoclicker
from environment.iteration1 import VisualStimuliChanger
from customPyACTR.middleman import get_middleman
import pyactr as actr

class BasicSimulation:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = actr.Environment(focus_position=(100, 100))
        self.active_agent_simulation = None
        self.active_agent_name = None

    def run_simulation(self, realtime=True, steps=1):
        # initialise
        middleman = get_middleman(self.environment)
        agent_one = Autoclicker.get_agent(self.environment, middleman, "A")
        agent_two = Autoclicker.get_agent(self.environment, middleman, "B")

        triggers = ['S', 'B', 'C', 'D']
        text = [
            {'K': {'text': 'K', 'position': (120, 140)}},
            {'B': {'text': 'B', 'position': (180, 240)}},
            {'C': {'text': 'C', 'position': (260, 200)}},
            {'D': {'text': 'D', 'position': (300, 160)}}
        ]

        # run the simulation
        agent_one_simulation = agent_one.simulation(realtime=realtime, environment_process=self.environment.environment_process,
                                            stimuli=text,
                                            triggers=triggers,
                                            times=1)
        agent_two_simulation = agent_two.simulation(realtime=realtime,
                                                    environment_process=self.environment.environment_process,
                                                    stimuli=text,
                                                    triggers=triggers,
                                                    times=1)

        self.active_agent_simulation = [agent_one_simulation, agent_two_simulation]
        self.active_agent_name = ["Darian", "Kjeld"]
        count = 0
        while count < 20:
            self.execute_step(middleman)
            count += 1

    def shift_left(self):
        if self.active_agent_simulation:
            self.active_agent_simulation = self.active_agent_simulation[1:] + [self.active_agent_simulation[0]]

        if self.active_agent_name:
            self.active_agent_name = self.active_agent_name[1:] + [self.active_agent_name[0]]

    def execute_step(self, middleman):
        self.active_agent_simulation[0].step()
        print(f"{self.active_agent_name[0]}, {self.active_agent_simulation[0].current_event}")
        event = self.active_agent_simulation[0].current_event

        if event[1] == "manual" and "KEY PRESSED:" in event[2]:
            middleman.motor_input_to_environment(event[2])
            self.shift_left()
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