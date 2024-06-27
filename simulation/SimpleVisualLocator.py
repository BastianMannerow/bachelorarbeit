from agents import VisualFinder
from environment import SimpleVisualEnvironment
from customPyACTR.middleman import get_middleman

class SimpleVisualLocator:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = SimpleVisualEnvironment.get_environment(self.width, self.height,
                                                                   focus_position=self.focus_position)

    def run_simulation(self, realtime=True, steps=1):
        stimuli, environment_stimuli_text = self.environment.get_stimuli()
        print(f"Stimuli: {environment_stimuli_text}")

        self.environment.print_matrix()  # Just to visualize the initial matrix state
        middleman = get_middleman(self.environment)
        agent = VisualFinder.get_agent(self.environment, middleman)
        simulation_agent = agent.simulation(realtime=realtime, environment_process=self.environment.environment_process,
                                            stimuli=environment_stimuli_text,
                                            triggers=stimuli,
                                            times=1)
        simulation_agent.run(steps)
