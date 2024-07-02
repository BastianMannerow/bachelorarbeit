import pyactr as actr

class Agent:
    def __init__(self, agent_type, environment, name):
        self.realtime = True
        self.actr_agent = agent_type

        self.simulation = agent_type.simulation(realtime=self.realtime,
                                                environment_process=environment.environment_process,
                                                stimuli=[],
                                                triggers=[],
                                                times=1)
        self.name = name

        def change_stimulus(self):
            new_triggers = ['X', 'Y', 'Z']
            new_text = [
                {'X': {'text': 'X', 'position': (100, 100)}},
                {'Y': {'text': 'Y', 'position': (200, 200)}},
                {'Z': {'text': 'Z', 'position': (300, 300)}}
            ]

            print("----------------------------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
            print("----------------------------------")
            self.simulation._Simulation__env.triggers = new_triggers
            self.simulation._Simulation__env.stimuli = new_text
            print("----------------------------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
            print("----------------------------------")


def build_agent(agent_type, environment, name):
    return Agent(agent_type, environment, name)

"""
initial_triggers = ['X', 'Y', 'Z']
initial_text_stimuli = [
    {'X': {'text': 'X', 'position': (100, 100)}},
    {'Y': {'text': 'Y', 'position': (200, 200)}},
    {'Z': {'text': 'Z', 'position': (300, 300)}}
]
"""