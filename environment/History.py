class History:
    def __init__(self):
        self.round_history = []
        self.round_counter = 0

    def start_new_round(self, round_number, initial_round=False):
        round_label = f'Runde{self.round_counter}'

        self.round_history.append({
            'label': round_label,  # Setze das Label entsprechend der aktuellen Runde
            'fortunes': {},        # Speichert das Vermögen jedes Agenten
            'nominations': [],     # Platzhalter für Nominierungen (Matrix)
            'punished': [],        # Platzhalter für bestrafte Agenten
            'rewarded': [],        # Platzhalter für belohnte Agenten
            'agent_decisions': {}, # Speichert Optionen und ausgewählte Optionen pro Agent
            'agent_cognition': {}  # Platzhalter für kognitive Informationen pro Agent
        })
        self.round_counter += 1

    def log_fortune(self, agent, fortune):
        # Speichere das Vermögen des Agenten unter dem Rundenlabel
        self.round_history[-1]['fortunes'][agent] = fortune

    def log_reward(self, agent):
        # Füge den Agenten der Liste der belohnten Agenten hinzu
        self.round_history[-1]['rewarded'].append(agent)

    def log_punish(self, agent):
        # Füge den Agenten der Liste der bestraften Agenten hinzu
        self.round_history[-1]['punished'].append(agent)

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
        self.round_history[-1]['nominations'] = nomination_matrix

    def log_agent_decision(self, agent, options, selected_option):
        # Speichere die Optionen und die ausgewählte Option für den Agenten
        self.round_history[-1]['agent_decisions'][agent] = {
            'options': options,
            'selected_option': selected_option
        }

    def log_agent_cognition(self, agent, cognition_data):
        # Speichere kognitive Informationen für den Agenten
        self.round_history[-1]['agent_cognition'][agent] = cognition_data

    def get_history(self):
        return self.round_history
