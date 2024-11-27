import random

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

    def contribute(self, agent, amount):
        # Only for Woche der KI
        names = {
            'A': "Giver",
            'B': "Spectator",
            'C': "Saboteur",
            'D': "Win Win",
            'E': "Neutral Profiteur",
            'F': "Egoist",
            'G': "Altruist",
            'H': "Self Destructive",
            'I': "Fatalist"
        }
        action = names.get(amount, "Unbekannter Typ")
        print(action)

        # Define reasons
        reasons = ["Reziprozität 1 Ordnung - Handeln", "Reziprozität 2 Ordnung - Status",
                   "Reziprozität 3 Ordnung - Soziale Norm"]

        # Generate three random percentages that sum to 100%
        cuts = sorted([random.randint(1, 99), random.randint(1, 99)])
        probabilities = [cuts[0], cuts[1] - cuts[0], 100 - cuts[1]]

        # Format reasons with probabilities for display
        reason_display = "\n".join([f"{reason}: {prob}%" for reason, prob in zip(reasons, probabilities)])
        print(reason_display)

        # Display the action and the formatted reason text in the GUI
        self.gui.show_agent_action(agent.name, action, reason_display)


        # Public Goods Game
        """
        self.pool += amount
        contribution_cost_factor = agent.get_contribution_cost_factor()
        agent.set_fortune(agent.get_fortune() - amount * contribution_cost_factor)
        # Log the contribution and agent's fortune in history
        self.history.log_contribution(agent, amount)
        """

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
                self.history.log_punish(target_agent)

        for target_agent, requesting_agents in self.reward_requests.items():
            if len(requesting_agents) >= majority_count and target_agent != "":
                print(f"Executing reward on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() + self.reward)
                self.history.log_reward(target_agent)

        # Speichere die Nominierungen unter dem Label der aktuellen Runde
        self.history.log_round_nominations(self.simulation.agent_list, self.punish_requests, self.reward_requests)

        # Pool und Requests zurücksetzen
        self.pool = 0
        self.punish_requests = {}
        self.reward_requests = {}
        self.gui.update_round()
