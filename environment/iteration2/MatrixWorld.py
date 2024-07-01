import pyactr as actr

class MatrixWorld(actr.Environment):
    def __init__(self, width, height, focus_position, agents=None):
        super().__init__(focus_position=focus_position)
        self.width = width
        self.height = height
        self.matrix = [[None for _ in range(width)] for _ in range(height)]
        self.agents = agents if agents is not None else []
        self.agent_positions = {}

    def move_agent_left(self, agent):
        pass

    def move_agent_right(self, agent):
        pass

    def move_agent_top(self, agent):
        pass

    def move_agent_bottom(self, agent):
        pass

    def attack_agent(self, agent):
        pass

    def cooperate_agent(self, agent):
        pass

    def eat_food(self, agent):
        pass

def get_environment(width, height, focus_position, agents=None):
    return MatrixWorld(width, height, focus_position, agents)