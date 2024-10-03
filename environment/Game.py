from gui.PublicGoodsGameGUI import PublicGoodsGameGUI

class Game:
    def __init__(self, reward, punishment, multiplication_factor, history, simulation, root):
        self.gui = PublicGoodsGameGUI(simulation, self, root)
        self.gui.update()
        self.reward = reward
        self.punishment = punishment
        self.multiplication_factor = multiplication_factor
        self.pool = 0
        self.simulation = simulation

        # Dictionaries to store punish and reward requests
        self.punish_requests = {}
        self.reward_requests = {}

        self.history = history
        self.round_counter = 1

    def contribute(self, agent, amount):
        self.pool += amount
        contribution_cost_factor = agent.get_contribution_cost_factor()
        agent.set_fortune(agent.get_fortune() - amount * contribution_cost_factor)
        # Log the contribution and agent's fortune in history
        self.history.log_contribution(agent, amount)

    def punish_agent(self, agent, target_agent):
        # Add punish request for the target agent
        if target_agent not in self.punish_requests:
            self.punish_requests[target_agent] = []
        self.punish_requests[target_agent].append(agent)

    def reward_agent(self, agent, target_agent):
        # Add reward request for the target agent
        if target_agent not in self.reward_requests:
            self.reward_requests[target_agent] = []
        self.reward_requests[target_agent].append(agent)

    def round_completed(self):
        majority_count = len(self.simulation.agent_list) // 2 + 1

        for target_agent, requesting_agents in self.punish_requests.items():
            if len(requesting_agents) >= majority_count and target_agent != "":
                print(f"Executing punishment on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() - self.punishment)

        for target_agent, requesting_agents in self.reward_requests.items():
            if len(requesting_agents) >= majority_count and target_agent != "":
                print(f"Executing reward on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() + self.reward)

        # Speichere die Nominierungen unter dem Label der Runde
        self.history.log_round_nominations(self.simulation.agent_list, self.punish_requests, self.reward_requests)

        # Speichere den Besitz jedes Agenten in der History
        agent_fortunes = {agent.name: agent.get_fortune() for agent in self.simulation.agent_list}
        self.history.log_fortunes(agent_fortunes)

        # Startet eine neue Runde für die nächste Runde
        self.history.start_new_round()

        # Erhöhe den Rundenzähler
        self.round_counter += 1

        # Pool und Requests zurücksetzen
        self.pool = 0
        self.punish_requests = {}
        self.reward_requests = {}
        self.gui.update_round()