class History:
    def __init__(self):
        self.round_history = []

    def start_new_round(self):
        # Füge eine neue Runde zur Historie hinzu
        self.round_history.append({
            'label': f'Runde{len(self.round_history) + 1}',  # Füge Label für die Runde hinzu
            'contributions': {},
            'fortunes': {},  # Speichert das Vermögen jedes Agenten
            'nominations': []  # Platzhalter für Nominierungen
        })

    def log_contribution(self, agent, amount):
        # Stelle sicher, dass eine Runde existiert
        if len(self.round_history) == 0:
            self.start_new_round()

        # Speichere den Beitrag und das Vermögen des Agenten unter dem Rundenlabel
        self.round_history[-1]['contributions'][agent.name] = amount
        self.round_history[-1]['fortunes'][agent.name] = agent.get_fortune()

    def log_round_nominations(self, agent_list, punish_requests, reward_requests):
        if len(self.round_history) == 0:
            self.start_new_round()

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
        self.round_history[-1]['nominations'] = nomination_matrix
        print(self.round_history)

    def log_fortunes(self, fortunes):
        # Stelle sicher, dass eine Runde existiert
        if len(self.round_history) == 0:
            self.start_new_round()

        # Speichere das Vermögen jedes Agenten unter dem Rundenlabel
        self.round_history[-1]['fortunes'] = fortunes

    def get_history(self):
        # Gibt die gesamte gespeicherte Historie zurück (jede Runde unter einem Label)
        return self.round_history
