from environment.AgentConstruct import AgentConstruct


class Middleman:
    def __init__(self, environment, simulation):
        self.experiment_environment = environment
        self.current_state = "Pending"
        self.target_agent = None
        self.amount = None
        self.simulation = simulation
        self.completed_actions = set()  # Track completed actions

    # Handles the agents inputs
    def motor_input(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()
        print(f"JO {filtered_string}")

        # Initially
        if self.current_state == "Pending":
            if filtered_string in ['R', 'P', 'C']:
                if filtered_string == 'R':
                    self.current_state = "Reward"
                elif filtered_string == 'P':
                    self.current_state = "Punish"
                elif filtered_string == 'C':
                    self.current_state = "Contribute"

                if self.current_state in self.completed_actions:
                    print(f"{self.current_state} action has already been completed. No duplicate actions allowed.")
                    self.current_state = "Pending"
                    return

                print(f"State changed to: {self.current_state}")
            else:
                print(f"The key input {filtered_string} was not defined for your environment.")
                return

        # Specific State Events
        else:
            if self.current_state in ["Reward", "Punish"]:
                # First, expect a letter to set the target agent
                if self.target_agent is None:
                    target_agent_letter = filtered_string.upper()  # Assume agents are mapped to letters
                    self.target_agent = agent.get_agent_dictionary().get(target_agent_letter)
                    if self.target_agent is None:
                        print(f"Agent {target_agent_letter} not found.")
                        return
                    print(f"Target agent set to: {self.target_agent.name}")
                else:
                    # Execute based on current state
                    if self.current_state == "Reward":
                        self.motor_input_to_environment('R', agent)
                    elif self.current_state == "Punish":
                        self.motor_input_to_environment('P', agent)

                    # Mark the action as completed
                    self.completed_actions.add(self.current_state)

                    # Reset
                    self.current_state = "Pending"
                    self.target_agent = None
                    self.amount = None

            elif self.current_state == "Contribute":
                self.amount = int(filtered_string)

                print(f"Amount set to: {self.amount}")
                self.motor_input_to_environment('C', agent)

                # Mark the action as completed
                self.completed_actions.add(self.current_state)

                # Reset
                self.current_state = "Pending"
                self.amount = None

        # Check if all actions are completed
        if len(self.completed_actions) == 3:
            self.simulation.next_turn()
            self.completed_actions.clear()

    def motor_input_to_environment(self, input_type, agent):
        if input_type == 'R':
            self.experiment_environment.reward(agent, self.target_agent, self.amount)
        elif input_type == 'P':
            self.experiment_environment.punish(agent, self.target_agent, self.amount)
        elif input_type == 'C':
            self.experiment_environment.contribute(agent, self.amount)

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