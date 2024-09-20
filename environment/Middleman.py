from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall
from agents.iteration2.AgentConstruct import AgentConstruct


class Middleman:
    def __init__(self, environment):
        self.experiment_environment = environment
        self.current_state = "Pending"  # Initialer Zustand ist Pending
        self.target_agent = None
        self.amount = None

    # Handles the agents inputs
    def motor_input(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()

        # Initially
        if self.current_state == "Pending":
            if filtered_string in ['R', 'P', 'C']:
                if filtered_string == 'R':
                    self.current_state = "Reward"
                elif filtered_string == 'P':
                    self.current_state = "Punish"
                elif filtered_string == 'C':
                    self.current_state = "Contribute"
                print(f"State changed to: {self.current_state}")
            else:
                print(f"The key input {filtered_string} was not defined for your environment.")

        # Specific State Events
        else:
            try:
                number = int(filtered_string)
                if number < 0 or number > 9:
                    raise ValueError("Number must be between 0 and 9.")
            except ValueError as e:
                print(e)
                return

            if self.current_state in ["Reward", "Punish"]:
                if self.target_agent is None:
                    self.target_agent = number
                    print(f"Target agent set to: {self.target_agent}")
                else:
                    self.amount = number
                    print(f"Amount set to: {self.amount}")

                    if self.current_state == "Reward":
                        self.motor_input_to_environment('R', agent)
                    elif self.current_state == "Punish":
                        self.motor_input_to_environment('P', agent)
                    # Reset
                    self.current_state = "Pending"
                    self.target_agent = None
                    self.amount = None
            elif self.current_state == "Contribute":
                self.amount = number
                print(f"Amount set to: {self.amount}")
                self.motor_input_to_environment('C', agent)
                # Reset
                self.current_state = "Pending"
                self.amount = None

    def motor_input_to_environment(self, input_type, agent):
        if input_type == 'R':
            if not self.experiment_environment.reward(agent, self.target_agent, self.amount):
                print("Reward Error")
        elif input_type == 'P':
            if not self.experiment_environment.punish(agent, self.target_agent, self.amount):
                print("Punishment Error")
        elif input_type == 'C':
            if not self.experiment_environment.contribute(agent, self.amount):
                print("Contribution Error")

    def set_environment(self, experiment_environment):
        self.experiment_environment = experiment_environment

    def get_agent_stimulus(self, agent):
        matrix = self.experiment_environment.get_matrix()
        r, c = self.experiment_environment.find_agent(agent)
        agent_stimuli_dictionary = agent.get_agent_dictionary()

        new_triggers = []
        new_text = {}

        rows = len(matrix)
        cols = len(matrix[0])

        # Initialize the visual stimuli matrix with empty strings
        visual_stimuli = [['' for _ in range(5)] for _ in range(5)]

        index = 0  # To keep track of the index for new_text

        for i in range(5):
            for j in range(5):
                matrix_i = r - 2 + i
                matrix_j = c - 2 + j
                if matrix_i < 0 or matrix_i >= rows or matrix_j < 0 or matrix_j >= cols:
                    visual_stimuli[i][j] = 'X'
                else:
                    elements = matrix[matrix_i][matrix_j]
                    for element in elements:
                        if isinstance(element, AgentConstruct):
                            for key, value in agent_stimuli_dictionary.items():
                                if value == element:
                                    new_triggers.append(key)
                                    new_text[index] = {'text': key, 'position': (matrix_i, matrix_j)}
                                    visual_stimuli[i][j] = key
                                    index += 1
                                    break
                        elif isinstance(element, Food):
                            if 'Y' not in new_triggers:
                                new_triggers.append('Y')
                            new_text[index] = {'text': 'Y', 'position': (matrix_i, matrix_j)}
                            visual_stimuli[i][j] = 'Y'
                            index += 1
                        elif isinstance(element, Wall):
                            if 'Z' not in new_triggers:
                                new_triggers.append('Z')
                            new_text[index] = {'text': 'Z', 'position': (matrix_i, matrix_j)}
                            visual_stimuli[i][j] = 'Z'
                            index += 1

        agent.set_visual_stimuli(visual_stimuli)

        return new_triggers, new_text


def get_middleman(environment):
    return Middleman(environment)