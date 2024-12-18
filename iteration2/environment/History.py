class History:
    def __init__(self):
        self.round_history = []
        self.round_counter = 0

    def start_new_round(self, round_number, initial_round=False):
        round_label = f'Runde{self.round_counter}'

        self.round_history.append({
            'label': round_label,   # Number of the round
            'fortunes': {},         # Fortune of each agent
            'nominations': [],      # Nomination matrix for reward and punishment
            'punished': [],         # Punished agents
            'rewarded': [],         # Rewarded agents
            'agent_decisions': {},  # Agents decisions
            'agent_cognition': {}   # Involved cognition for each agent
        })
        self.round_counter += 1

    # Fortune of each agent
    def log_fortune(self, agent, fortune):
        self.round_history[-1]['fortunes'][agent] = fortune

    # Rewarded agents
    def log_reward(self, agent):
        self.round_history[-1]['rewarded'].append(agent)

    # Punished agents
    def log_punish(self, agent):
        self.round_history[-1]['punished'].append(agent)

    # Nomination matrix for reward and punishment
    def log_round_nominations(self, agent_list, punish_requests, reward_requests):
        num_agents = len(agent_list)
        nomination_matrix = [['-' for _ in range(num_agents)] for _ in range(num_agents)]

        # Punishment
        for target_agent, requesting_agents in punish_requests.items():
            if target_agent not in agent_list:
                print(f"Warning: Target agent {target_agent} is not in the agent list")
                continue
            for agent in requesting_agents:
                if agent in agent_list:
                    nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'P'

        # Reward
        for target_agent, requesting_agents in reward_requests.items():
            if target_agent not in agent_list:
                print(f"Warning: Target agent {target_agent} is not in the agent list")
                continue
            for agent in requesting_agents:
                if agent in agent_list:
                    nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'R'

        # Store nomination matrix for reward & punishment
        self.round_history[-1]['nominations'] = nomination_matrix

        # Store fortunes of each agent
        for agent in agent_list:
            if hasattr(agent, 'get_fortune') and callable(agent.get_fortune):
                self.log_fortune(agent, agent.get_fortune())
            else:
                print(f"Warning: Agent {agent} does not have a callable 'get_fortune' method")

    # Agents decisions
    def log_agent_decision(self, agent, options, selected_option):
        self.round_history[-1]['agent_decisions'][agent] = {
            'options': options,
            'selected_option': selected_option
        }

    # Involved cognition for each agent
    def log_agent_cognition(self, agent, cognition_data):
        self.round_history[-1]['agent_cognition'][agent] = cognition_data

    def get_history(self):
        return self.round_history
