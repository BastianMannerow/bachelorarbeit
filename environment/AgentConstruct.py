import pyactr as actr


class AgentConstruct:
    def __init__(self, agent_type, actr_environment, middleman, name, name_number, fortune, contribution_cost_factor,
                 print_trace):
        self.print_trace = print_trace
        # ACT-R specific settings
        self.realtime = False
        self.actr_agent = agent_type
        self.actr_environment = actr_environment
        self.simulation = None if agent_type is None else agent_type.simulation(
            realtime=self.realtime,
            environment_process=actr_environment.environment_process,
            stimuli=[{'S': {'text': 'S', 'position': (1, 1)}}],
            triggers=['S'],
            times=0.1,
            gui=False,
            trace=print_trace
        )

        # Simulation specific settings
        self.middleman = middleman
        self.name = name
        self.name_number = name_number
        self.agent_dictionary = None
        self.visual_stimuli = []
        self.print_stimulus = False
        self.print_trace = print_trace

        # Public Goods Game specific values
        self.fortune = fortune
        self.contribution_cost_factor = contribution_cost_factor

    def update_stimulus(self):
        if self.actr_agent:
            try:
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
            except:
                print("ACT-R Stimulus wurde nicht überschrieben.")

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

    def set_fortune(self, fortune):
        self.fortune = fortune

    def get_fortune(self):
        return self.fortune

    def get_contribution_cost_factor(self):
        return self.contribution_cost_factor

    def reset_simulation(self):
        dd = {actr.chunkstring(string="\
            isa option\
            type giver"): [0], actr.chunkstring(string="\
            isa option\
            type altruist"): [0],
            actr.chunkstring(string="\
            isa option\
            type test"): [0],
            actr.chunkstring(string="\
            isa option\
            type blabla"): [0]}
        self.actr_agent.decmems = {}
        self.actr_agent.set_decmem(dd)

        print(f"---------------------------- HIER{self.actr_agent.goal}")
        self.actr_agent.goal.add(actr.chunkstring(string="isa selectContribute state start"))
        self.simulation = self.actr_agent.simulation(
            realtime=self.realtime,
            environment_process=self.actr_environment.environment_process,
            stimuli=[{'S': {'text': 'S', 'position': (1, 1)}}],
            triggers=['S'],
            times=0.1,
            gui=False,
            trace=self.print_trace
        )

    def handle_empty_schedule(self):
        # 1. new simulation and goal
        print("Empty Schedule. Reset to initial goal.")
        self.reset_simulation()
        print(f"Current Memory of {self.name}: {self.actr_agent.decmems}")
        print(f"New Goal: {self.actr_agent.goal}")

    def handle_new_round(self):
        if self.actr_agent:
            # self.actr_agent.decmems = {}
            # .actr_agent.set_decmem(dd)

            print(f"Current Memory of {self.name}: {self.actr_agent.decmems}")

            # refresh declarative memory and reset goal
            self.reset_simulation()
