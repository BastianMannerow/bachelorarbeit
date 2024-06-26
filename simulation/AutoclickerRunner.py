from agents import Autoclicker
from environment import SimpleMatrixEnvironment
from customPyACTR.middleman import get_middleman

class AutoClickerRunner:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = SimpleMatrixEnvironment.get_environment(self.width, self.height,
                                                                   focus_position=self.focus_position)

    def run_simulation(self, realtime=True, steps=1):
        self.environment.print_matrix()  # Just to visualize the initial matrix state
        middleman = get_middleman(self.environment)
        print(middleman)
        agent = Autoclicker.get_agent(None, middleman)
        simulation_agent = agent.simulation(realtime=realtime, environment_process=self.environment.environment_process)

        simulation_agent.run(steps)
