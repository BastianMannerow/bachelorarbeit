from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall
from agents.iteration2.AgentBuilder import AgentBuilder

class Middleman:
    def __init__(self, environment):
        self.experiment_environment = environment

    def motor_input_to_environment(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()

        def move_right():
            if not self.experiment_environment.move_agent_right(agent):
                print("Movement Blocked")

        def move_left():
            if not self.experiment_environment.move_agent_left(agent):
                print("Movement Blocked")

        def move_up():
            if not self.experiment_environment.move_agent_up(agent):
                print("Movement Blocked")

        def move_down():
            if not self.experiment_environment.move_agent_down(agent):
                print("Movement Blocked")

        switch_case = {
            'D': move_right,
            'A': move_left,
            'W': move_up,
            'S': move_down
        }

        if filtered_string in switch_case:
            switch_case[filtered_string]()
        else:
            print(f"The key input {filtered_string} was not defined for your environment.")

    def set_environment(self, experiment_environment):
        self.experiment_environment = experiment_environment

    def get_agent_stimulus(self, agent):
        matrix = self.experiment_environment.get_matrix()
        r, c = self.experiment_environment.find_agent(agent)
        agent_stimuli_dictionary = agent.get_agent_dictionary()

        new_triggers = []
        new_text = []

        rows = len(matrix)
        cols = len(matrix[0])

        for i in range(max(0, r - 2), min(rows, r + 3)):
            for j in range(max(0, c - 2), min(cols, c + 3)):
                elements = matrix[i][j]
                for element in elements:
                    if isinstance(element, AgentBuilder):
                        for key, value in agent_stimuli_dictionary.items():
                            if value == element:
                                new_triggers.append(key)
                                new_text.append({key: {'text': key, 'position': (i, j)}})
                                break
                    elif isinstance(element, Food):
                        if 'Y' not in new_triggers:
                            new_triggers.append('Y')
                        new_text.append({'Y': {'text': 'Y', 'position': (i, j)}})
                    elif isinstance(element, Wall):
                        if 'Z' not in new_triggers:
                            new_triggers.append('Z')
                        new_text.append({'Z': {'text': 'Z', 'position': (i, j)}})

        return new_triggers, new_text

def get_middleman(environment):
    return Middleman(environment)