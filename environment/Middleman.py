from environment.AgentConstruct import AgentConstruct


class Middleman:
    def __init__(self, environment, simulation, print_middleman):
        self.experiment_environment = environment
        self.current_state = "Pending"
        self.target_agent = None
        self.amount = None
        self.simulation = simulation
        self.completed_actions = set()  # Track completed actions
        self.print_middleman = print_middleman

    # Overrides the environment if needed
    def set_environment(self, experiment_environment):
        self.experiment_environment = experiment_environment

    # Handles the agents inputs
    def motor_input(self, input, agent):
        filtered_string = input.split("KEY PRESSED:")[-1].strip()
        if self.print_middleman:
            print(f"Agent: {agent.name}, Input: {filtered_string}")

        # Initially (Zustandswechsel)
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

                if self.print_middleman:
                    print(f"State changed to: {self.current_state}")
            else:
                print(f"The key input {filtered_string} was not defined for your environment.")
                return

        # Specific State Events (Agentenwahl oder Beitrag)
        else:
            if self.current_state in ["Reward", "Punish"]:
                if self.target_agent is None:
                    target_agent_letter = filtered_string.upper()  # Assume agents are mapped to letters
                    self.target_agent = agent.get_agent_dictionary().get(target_agent_letter)

                    # Check for specific input 'Z'
                    if target_agent_letter == 'Z':
                        self.target_agent = ""
                    elif self.target_agent is None:
                        print(f"Agent {target_agent_letter} not found.")
                        return
                    else:
                        print(f"Target agent set to: {self.target_agent.name}")

                    # Perform the action after selecting the target
                    if self.current_state == "Reward":
                        self.motor_input_to_environment('R', agent)
                    elif self.current_state == "Punish":
                        self.motor_input_to_environment('P', agent)

                    # Mark action as completed
                    self.completed_actions.add(self.current_state)

                    # Reset state
                    self.current_state = "Pending"
                    self.target_agent = None

            elif self.current_state == "Contribute":
                try:
                    self.amount = filtered_string
                    if self.print_middleman:
                        print(f"Amount set to: {self.amount}")
                    self.motor_input_to_environment('C', agent)

                    # Mark action as completed
                    self.completed_actions.add(self.current_state)

                    # Reset state
                    self.current_state = "Pending"
                    self.amount = None
                except ValueError:
                    print(f"Invalid amount: {filtered_string}")
                    return

        # Check if all actions are completed (Reward, Punish, Contribute)
        if len(self.completed_actions) == 3:
            self.simulation.next_turn()
            self.completed_actions.clear()

    def motor_input_to_environment(self, input_type, agent):
        if input_type == 'R':
            self.experiment_environment.reward_agent(agent, self.target_agent)
        elif input_type == 'P':
            self.experiment_environment.punish_agent(agent, self.target_agent)
        elif input_type == 'C':
            self.experiment_environment.contribute(agent, self.amount)

    # Generates agents visual stimuli based on the environment and the agents dictionary for other agents.
    def get_agent_stimulus(self, agent):
        """
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
        """
        new_triggers = None
        new_text = None

        return new_triggers, new_text

    # If notified by the simulation, the method will notify all agents, that the round is completed.
    def round_completed(self):
        for agent in self.simulation.agent_list:
            agent.handle_new_round()
