from gui.iteration2.MatrixWorldGUI import MatrixWorldGUI

class Game:
    def __init__(self, transparency, reward, punishment, multiplication_factor, agent_list, root):
        self.gui = MatrixWorldGUI(self, root)
        self.gui.update()
        self.transparency = transparency
        self.reward = reward
        self.punishment = punishment
        self.multiplication_factor = multiplication_factor
        self.agent_list = agent_list
        self.pool = 0

        # Dictionaries to store punish and reward requests
        self.punish_requests = {}
        self.reward_requests = {}

    def contribute(self, agent, amount):
        self.pool += amount
        contribution_cost_factor = agent.get_contribution_cost_factor
        agent.set_fortune(agent.get_fortune() - amount * contribution_cost_factor)

    def punish(self, agent, target_agent):
        # Add punish request for the target agent
        if target_agent not in self.punish_requests:
            self.punish_requests[target_agent] = []
        self.punish_requests[target_agent].append(agent)

    def reward(self, agent, target_agent):
        # Add reward request for the target agent
        if target_agent not in self.reward_requests:
            self.reward_requests[target_agent] = []
        self.reward_requests[target_agent].append(agent)

    def round_completed(self):
        # Determine how many agents must request a punish/reward for it to be executed
        majority_count = len(self.agent_list) // 2 + 1

        # Execute punishments if more than half of the agents requested it
        for target_agent, requesting_agents in self.punish_requests.items():
            if len(requesting_agents) >= majority_count:
                print(f"Executing punishment on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() - self.punishment)

        # Execute rewards if more than half of the agents requested it
        for target_agent, requesting_agents in self.reward_requests.items():
            if len(requesting_agents) >= majority_count:
                print(f"Executing reward on {target_agent.name}")
                target_agent.set_fortune(target_agent.get_fortune() + self.reward)

        # Reset pool and requests after each round
        self.pool = 0
        self.punish_requests = {}
        self.reward_requests = {}

def get_environment(transparency, reward, punishment, multiplication_factor, agent_list, root):
    return Game(transparency, reward, punishment, multiplication_factor, agent_list, root)
