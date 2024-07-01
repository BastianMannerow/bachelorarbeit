from agents.iteration1 import Autoclicker
from environment.iteration1 import SimpleMultipleAgentEnvironment
from customPyACTR.middleman import get_middleman
import time

class DifferentAgentStepper:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = SimpleMultipleAgentEnvironment.get_environment(self.width, self.height,
                                                                          focus_position=self.focus_position,
                                                                          agents=None)

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

        # print event
        count = 0
        while count < 40:
            try:
                # do one simulation step
                agent_one_simulation.step()
                print("AGENT 1, ", agent_one_simulation.current_event)
                time.sleep(1)
                agent_two_simulation.step()
                print("AGENT 2, ", agent_two_simulation.current_event)
                count += 1
            except Exception as e:
                print("Error:", e)
                break
