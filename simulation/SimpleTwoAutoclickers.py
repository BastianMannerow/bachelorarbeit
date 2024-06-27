import threading

from agents import Autoclicker
from environment import SimpleMultipleAgentEnvironment
from customPyACTR.middleman import get_middleman

class SimpleTwoAutoclickers:
    def __init__(self, width, height, focus_position):
        self.width = width
        self.height = height
        self.focus_position = focus_position
        self.environment = SimpleMultipleAgentEnvironment.get_environment(self.width, self.height,
                                                                          focus_position=self.focus_position, agents=None)
        self.run_event = threading.Event()
        self.run_event.set()  # Start with thread one

    def run_simulation(self, realtime=True, steps=1):
        self.environment.print_matrix()  # Just to visualize the initial matrix state
        middleman = get_middleman(self.environment)

        agent_one = Autoclicker.get_agent(None, middleman, "A")
        agent_two = Autoclicker.get_agent(None, middleman, "B")
        self.environment.set_agents([agent_one, agent_two])

        simulation_agent_one = agent_one.simulation(realtime=realtime, environment_process=self.environment.environment_process)
        simulation_agent_two = agent_two.simulation(realtime=realtime, environment_process=self.environment.environment_process)

        # Threading for both simulations
        thread_one = threading.Thread(target=self.execution, args=(simulation_agent_one, steps, "one"))
        thread_two = threading.Thread(target=self.execution, args=(simulation_agent_two, steps, "two"))

        thread_one.start()
        thread_two.start()

    def execution(self, agent, steps, thread_id):
        while True:
            self.run_event.wait()  # wait till the event was set
            if thread_id == "one":
                agent.run(steps)
                self.run_event.clear()
            else:
                agent.run(steps)
                self.run_event.set()

    def switch_threads(self):
        if self.run_event.is_set():
            self.run_event.clear()
        else:
            self.run_event.set()