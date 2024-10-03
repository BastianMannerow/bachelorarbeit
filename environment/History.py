class History:
    def __init__(self):
        self.round_history = []
        self.round_counter = 0

    def start_new_round(self, round_number, initial_round=False):
        round_label = f'Runde{self.round_counter}'
        print(round_label)

        self.round_history.append({
            'label': round_label,  # Setze das Label entsprechend der übergebenen Rundennummer
            'contributions': {},
            'fortunes': {},        # Speichert das Vermögen jedes Agenten
            'nominations': [],     # Platzhalter für Nominierungen
            'punished': [],        # Platzhalter für bestrafte Agenten
            'rewarded': []         # Platzhalter für belohnte Agenten
        })
        self.round_counter = self.round_counter + 1

    def log_contribution(self, agent, amount):
        # Speichere den Beitrag und das Vermögen des Agenten unter dem Rundenlabel
        self.round_history[-1]['contributions'][agent.name] = amount
        self.round_history[-1]['fortunes'][agent.name] = agent.get_fortune()

    def log_reward(self, agent):
        # Füge den Agenten der Liste der belohnten Agenten hinzu
        self.round_history[-1]['rewarded'].append(agent.name)

    def log_punish(self, agent):
        # Füge den Agenten der Liste der bestraften Agenten hinzu
        self.round_history[-1]['punished'].append(agent.name)


    def log_round_nominations(self, agent_list, punish_requests, reward_requests):
        num_agents = len(agent_list)
        nomination_matrix = [['-' for _ in range(num_agents)] for _ in range(num_agents)]

        # Verarbeite die Bestrafungsanfragen
        for target_agent, requesting_agents in punish_requests.items():
            if target_agent not in agent_list:
                print(f"Warning: Target agent {target_agent} is not in the agent list")
                continue
            for agent in requesting_agents:
                if agent in agent_list:
                    nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'P'

        # Verarbeite die Belohnungsanfragen
        for target_agent, requesting_agents in reward_requests.items():
            if target_agent not in agent_list:
                print(f"Warning: Target agent {target_agent} is not in the agent list")
                continue
            for agent in requesting_agents:
                if agent in agent_list:
                    nomination_matrix[agent_list.index(agent)][agent_list.index(target_agent)] = 'R'

        # Füge die Nominierungen zur aktuellen Runde hinzu
        print(self.round_history)
        self.round_history[-1]['nominations'] = nomination_matrix
        print(self.round_history)


    def get_history(self):
        return self.round_history
