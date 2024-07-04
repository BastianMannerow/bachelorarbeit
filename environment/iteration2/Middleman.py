from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall
from agents.iteration2.AgentBuilder import AgentBuilder

class Middleman:
    def __init__(self, environment):
        self.experiment_environment = environment

    def motor_input_to_environment(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()
        print(f"{agent.get_agent_name()} chose to press {filtered_string}.")

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

        def be_ready():
            print("Agent initialised.")

        switch_case = {
            'D': move_right,
            'A': move_left,
            'W': move_up,
            'S': move_down,
            'SPACE': be_ready
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

        # Initialize the visual stimuli matrix with empty strings
        visual_stimuli = [['' for _ in range(5)] for _ in range(5)]

        for i in range(5):
            for j in range(5):
                matrix_i = r - 2 + i
                matrix_j = c - 2 + j
                if matrix_i < 0 or matrix_i >= rows or matrix_j < 0 or matrix_j >= cols:
                    visual_stimuli[i][j] = 'X'
                else:
                    elements = matrix[matrix_i][matrix_j]
                    for element in elements:
                        if isinstance(element, AgentBuilder):
                            for key, value in agent_stimuli_dictionary.items():
                                if value == element:
                                    new_triggers.append(key)
                                    new_text.append({key: {'text': key, 'position': (matrix_i, matrix_j)}})
                                    visual_stimuli[i][j] = key
                                    break
                        elif isinstance(element, Food):
                            if 'Y' not in new_triggers:
                                new_triggers.append('Y')
                            new_text.append({'Y': {'text': 'Y', 'position': (matrix_i, matrix_j)}})
                            visual_stimuli[i][j] = 'Y'
                        elif isinstance(element, Wall):
                            if 'Z' not in new_triggers:
                                new_triggers.append('Z')
                            new_text.append({'Z': {'text': 'Z', 'position': (matrix_i, matrix_j)}})
                            visual_stimuli[i][j] = 'Z'

        agent.set_visual_stimuli(visual_stimuli)



        return new_triggers, new_text


def get_middleman(environment):
    return Middleman(environment)