import random

class AgentConstruct:
    def __init__(self, agent_type, human, actr_environment, middleman, name, name_number, fortune, contribution_cost):
        # ACT-R specific settings
        self.realtime = False
        self.actr_agent = agent_type
        self.simulation = agent_type.simulation(realtime=self.realtime,
                                                environment_process=actr_environment.environment_process,
                                                stimuli=[
                                                            {'S': {'text': 'S', 'position': (1, 1)}}
                                                        ],
                                                triggers=['S'],
                                                times=0.1,
                                                gui=False
                                                )
        # Simulation specific settings
        self.human = human
        self.middleman = middleman
        self.name = name
        self.name_number = name_number
        self.agent_dictionary = None
        self.visual_stimuli = []
        self.print_stimulus = False

        # Public Goods Game specific values
        self.fortune = fortune
        self.contribution_cost = contribution_cost

    def update_stimulus(self):
        new_triggers, new_text = self.middleman.get_agent_stimulus(self)

        if (self.print_stimulus):
            print("----------------- OLD STIMULUS -----------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
        self.simulation._Simulation__env.triggers = new_triggers
        self.simulation._Simulation__env.stimuli = new_text
        # self.simulation._Simulation__env.trigger = new_triggers #  Seems to make problems.
        self.simulation._Simulation__env.stimulus = new_text

        if (self.print_stimulus):
            print("----------------- NEW STIMULUS -----------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
            print("----------------- SINGLE STIMULUS -----------------")
            print(f"{self.simulation._Simulation__env.stimulus}")


    def set_agent_dictionary(self, agent_list):
        if len(agent_list) > 20:
            raise ValueError("Only 20 agent are currently supported")

        # Ensure the agent is at the beginning and receives the letter A
        agent_list = [self] + [agent for agent in agent_list if agent != self]

        # Create the dictionary with letters as keys
        self.agent_dictionary = {chr(65 + i): agent for i, agent in enumerate(agent_list)}

    def get_agent_dictionary(self):
        return self.agent_dictionary

    def get_name_number(self):
        return self.name_number

    def get_agent_name(self):
        return self.name

    def set_visual_stimuli(self, visual_stimuli):
        self.visual_stimuli = visual_stimuli

    def get_visual_stimuli(self):
        return self.visual_stimuli


def build_agent(agent_type, environment, middleman, name, name_number):
    return AgentConstruct(agent_type, environment, middleman, name, name_number)