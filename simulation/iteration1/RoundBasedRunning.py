from agents.iteration1 import Autoclicker
from environment.iteration1 import SimpleMultipleAgentEnvironment
from customPyACTR.middleman import get_middleman

class RoundBasedRunning:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = SimpleMultipleAgentEnvironment.get_environment(self.width, self.height,
                                                                          focus_position=self.focus_position,
                                                                          agents=None)
        self.active_agent_simulation = None
        self.active_agent_name = None

    def run_simulation(self, realtime=True, steps=1):
        # initialise
        middleman = get_middleman(self.environment)
        agent_one = Autoclicker.get_agent(None, middleman, "A")
        agent_two = Autoclicker.get_agent(None, middleman, "B")
        self.environment.set_agents([agent_one, agent_two])

        # run the simulation
        agent_one_simulation = agent_one.simulation(realtime=False, times=3)
        agent_two_simulation = agent_two.simulation(realtime=False, times=3)

        # simulation_agent = agent_one.simulation(realtime=realtime, environment_process=self.environment.environment_process)
        # simulation_agent.run(steps)

        self.active_agent_simulation = [agent_one_simulation, agent_two_simulation]
        self.active_agent_name = ["Boris", "Vlad"]
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