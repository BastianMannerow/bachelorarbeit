import random

from iteration2.gui.PublicGoodsGameGUI import PublicGoodsGameGUI

class Game:
    def __init__(self, reward, punishment, multiplication_factor, history, simulation, root):
        self.reward = reward
        self.punishment = punishment
        self.multiplication_factor = multiplication_factor
        self.pool = 0
        self.simulation = simulation

        # Dictionaries to store punish and reward requests
        self.punish_requests = {}
        self.reward_requests = {}

        self.history = history

        # Current dictionary to store the agents possible and selected decisions
        self.current_agent_choices = {}

    # Adding current agent choices
    def add_choice(self, choices, agent):
        self.current_agent_choices[agent] = {
            'options': choices,
            'selected_option': None
        }

    # Adding current agents final decision
    def add_decision(self, agent, selected_option):
        if agent in self.current_agent_choices:
            self.current_agent_choices[agent]['selected_option'] = selected_option
        else:
            print(f"Error: No choices recorded for agent {agent}")

    def contribute(self, agent, amount):
        # Public Goods Game
        self.pool = self.pool + amount
        contribution_cost_factor = agent.get_contribution_cost_factor()
        agent.set_fortune(agent.get_fortune() - amount * contribution_cost_factor)

    # Save punishment request from an agent
    def punish_agent(self, agent, target_agent):
        # Add punish request for the target agent
        if target_agent not in self.punish_requests:
            self.punish_requests[target_agent] = []
        self.punish_requests[target_agent].append(agent)

    # Save reward request from an agent
    def reward_agent(self, agent, target_agent):
        # Add reward request for the target agent
        if target_agent not in self.reward_requests:
            self.reward_requests[target_agent] = []
        self.reward_requests[target_agent].append(agent)

    # If all agents made their decisions,execute them. Executing them right away would cause synch errors
    def round_completed(self):
        majority_count = len(self.simulation.agent_list) // 2 + 1
        # Punishment
        if self.simulation.allow_punishment:
            for target_agent, requesting_agents in self.punish_requests.items():
                if target_agent != "" and len(requesting_agents) > 0:
                    punishment_value = self.punishment * len(
                        requesting_agents)
                    #print(f"Executing punishment on {target_agent.name} with {len(requesting_agents)} requests")
                    target_agent.set_fortune(target_agent.get_fortune() - punishment_value)
                    self.history.log_punish(target_agent)

        # Reward
        for target_agent, requesting_agents in self.reward_requests.items():
            if len(requesting_agents) >= majority_count and target_agent != "":
                #print(f"Executing reward on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() + self.reward)
                self.history.log_reward(target_agent)

        # Execute strategies
        self.execute_all_decisions()

        # Saving the data
        self.history.log_round_nominations(self.simulation.agent_list, self.punish_requests, self.reward_requests)
        for agent, decision_data in self.current_agent_choices.items():
            options = decision_data['options']
            selected_option = decision_data['selected_option']
            self.history.log_agent_decision(agent, options, selected_option)

        # Reset for new round
        self.pool = 0
        self.punish_requests = {}
        self.reward_requests = {}
        self.current_agent_choices = {}

    # Execute Strategy of each agent
    def execute_all_decisions(self):
        all_contributions = []
        for agent, choices in self.current_agent_choices.items():
            selected_option = choices.get('selected_option')
            amount = selected_option.get('id')

            if amount is not None:
                self.contribute(agent, amount)
                all_contributions.append(amount)
        average_contribution = sum(all_contributions) / len(all_contributions) if all_contributions else 0
        #print(f"Average Contribution: {average_contribution}")

        self.simulation.middleman.current_social_norm = average_contribution

        # Payout pool
        payment_list = self.simulation.agent_list
        benefit = (self.pool * self.multiplication_factor) / len(payment_list)
        for agent in payment_list:
            agent.set_fortune(agent.get_fortune() + benefit)

    def add_punish_request(self, agent_id, punish_targets):
        """
        Speichert Bestrafungsanfragen eines Agenten.

        :param agent_id: Die ID des Agenten, der die Anfragen stellt.
        :param punish_targets: Eine Liste von Agenten-IDs, die bestraft werden sollen.
        """
        if agent_id not in self.punish_requests:
            self.punish_requests[agent_id] = []
        self.punish_requests[agent_id].extend(punish_targets)

    def add_reward_request(self, agent_id, reward_targets):
        """
        Speichert Belohnungsanfragen eines Agenten.

        :param agent_id: Die ID des Agenten, der die Anfragen stellt.
        :param reward_targets: Eine Liste von Agenten-IDs, die belohnt werden sollen.
        """
        if agent_id not in self.reward_requests:
            self.reward_requests[agent_id] = []
        self.reward_requests[agent_id].extend(reward_targets)