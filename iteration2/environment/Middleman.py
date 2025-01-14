import math

class Middleman:
    def __init__(self, environment, simulation, print_middleman, current_social_norm):
        self.experiment_environment = environment
        self.current_state = "Pending"
        self.target_agent = None
        self.amount = None
        self.simulation = simulation
        self.completed_actions = set()  # Track completed actions
        self.print_middleman = print_middleman
        self.current_social_norm = current_social_norm

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
                    if agent.get_agent_dictionary().get(target_agent_letter):
                        self.target_agent = agent.get_agent_dictionary().get(target_agent_letter)["agent"]

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

    # If notified by the simulation, the method will notify all agents, that the round is completed.
    def round_completed(self):
        for agent in self.simulation.agent_list:
            agent.handle_new_round()

    # Generates all possible options to select from for all agents
    def choice_generator(self, agent):
        current_social_norm = self.current_social_norm
        multiplication_factor = self.experiment_environment.multiplication_factor
        possibilities = {}

        for agent_obj, agent_data in agent.agent_dictionary.items():
            # Determine the number of possible decisions based on fortune (floored to int if float)
            decision_count = math.floor(agent_data['agent'].get_fortune())
            decision_count = min(decision_count, self.simulation.contribution_limit)

            agent_dict = agent_data['agent'].agent_dictionary
            other_agents = [key for key in agent_dict.keys() if key != agent_obj]

            possibilities[agent_obj] = []
            for i in range(decision_count + 1):
                # Calculation of mean
                contribution_sum = (i + len(other_agents) * current_social_norm) * multiplication_factor
                distributed_sum = contribution_sum / (len(other_agents) + 1)

                # Adding possible id and fortune changes in the dictionary
                decision = {
                    "id": i,
                    **{
                        key: (
                                agent_dict[key]['agent'].get_fortune()
                                + distributed_sum
                                - (i if key == agent_obj else current_social_norm)
                        )
                        for key in agent_dict.keys()
                    }
                }
                possibilities[agent_obj].append(decision)

        # Notify the experiment environment and return the possibilities
        self.experiment_environment.add_choice(possibilities[list(possibilities.keys())[0]], agent)
        return possibilities

    # Returns the history of the last round
    def return_agents_history(self):
        last_round = self.simulation.history.round_history[self.simulation.history.round_counter-1]
        if 'agent_decisions' in last_round:
            return last_round['agent_decisions']
        else:
            print("No agent decisions found in the last round.")
            return None

    # Temporary solution to handle the agents decisions
    def nominate_for_reward(self, agent):
        extra_reward_list = agent.extra_reward_list
        extra_reward_list = agent.replace_letters_with_agents(extra_reward_list)
        self.experiment_environment.add_reward_request(agent, extra_reward_list)

    def nominate_for_punishment(self, agent, target_agent):
        self.experiment_environment.add_punish_request(agent, [target_agent])

    def login_final_choice(self, agent, choice):
        self.experiment_environment.add_decision(agent, choice)
        self.simulation.next_turn()
        self.completed_actions.clear()