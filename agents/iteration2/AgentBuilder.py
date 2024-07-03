
class AgentBuilder:
    def __init__(self, agent_type, actr_environment, middleman, name, name_number):
        self.realtime = True
        self.actr_agent = agent_type
        self.simulation = agent_type.simulation(realtime=self.realtime,
                                                environment_process=actr_environment.environment_process,
                                                stimuli=[],
                                                triggers=[],
                                                times=1)
        self.middleman = middleman
        self.name = name
        self.name_number = name_number
        self.agent_dictionary = None
        self.visual_stimuli = []

        self.print_stimulus = False

    def update_stimulus(self):
        new_triggers, new_text = self.middleman.get_agent_stimulus(self)
        if(self.print_stimulus):
            print("----------------- OLD STIMULUS -----------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
        self.simulation._Simulation__env.triggers = new_triggers
        self.simulation._Simulation__env.stimuli = new_text
        if (self.print_stimulus):
            print("----------------- NEW STIMULUS -----------------")
            print(f"{self.simulation._Simulation__env.triggers}")
            print(f"{self.simulation._Simulation__env.stimuli}")
            print("----------------------------------")

    def set_agent_dictionary(self, agent_list):
        if len(agent_list) > 20:
            raise ValueError("Only 20 agents are currently supported")

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
    return AgentBuilder(agent_type, environment, middleman, name, name_number)