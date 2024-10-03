class History:
    def __init__(self):
        # Liste, um die Geschichte pro Runde zu speichern
        self.round_history = []

    def log_contribution(self, agent, amount):
        if len(self.round_history) == 0 or 'contributions' not in self.round_history[-1]:
            self.round_history.append({
                'contributions': {},
                'fortunes': {},
                'nominations': []
            })

        self.round_history[-1]['contributions'][agent.name] = amount
        # Speichere das aktuelle Vermögen des Agenten
        self.round_history[-1]['fortunes'][agent.name] = agent.get_fortune()

    def log_round_nominations(self, agent_list, punish_requests, reward_requests):
        num_agents = len(agent_list)
        nomination_matrix = [['-' for _ in range(num_agents)] for _ in range(num_agents)]

        for target_agent, requesting_agents in punish_requests.items():
            for agent in requesting_agents:
                nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'P'

        for target_agent, requesting_agents in reward_requests.items():
            for agent in requesting_agents:
                nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'R'

        self.round_history[-1]['nominations'] = nomination_matrix

    def get_history(self):
        return self.round_history