import customPyACTR as actr

class SimpleMultipleAgentEnvironment(actr.Environment):
    def __init__(self, width, height, focus_position, agents=None):
        super().__init__(focus_position=focus_position)
        self.width = width
        self.height = height
        self.matrix = [[None for _ in range(width)] for _ in range(height)]
        self.agents = agents if agents is not None else []
        self.agent_positions = {}
        self.agent_symbols = {}  # Dictionary to store symbols for each agent

        self.initialize_agents()

    def initialize_agents(self):
        # Initialize agent positions and assign symbols
        for index, agent in enumerate(self.agents):
            position = (0, index)  # Agents start in the first column and different rows
            self.agent_positions[agent] = position
            symbol = chr(65 + index)  # Assign alphabetic letters starting from 'A'
            self.agent_symbols[agent] = symbol
            self.matrix[position[1]][position[0]] = symbol

    def update_position(self, agent, new_position):
        old_x, old_y = self.agent_positions[agent]
        new_x, new_y = new_position

        # Check if the position is within boundaries
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.matrix[old_y][old_x] = None
            self.matrix[new_y][new_x] = self.agent_symbols[agent]
            self.agent_positions[agent] = new_position

    def move_agent_right(self, symbol):
        agent = None
        for ag, sym in self.agent_symbols.items():
            if sym == symbol:
                agent = ag
                break

        if agent:
            old_x, old_y = self.agent_positions[agent]
            new_x = old_x + 1
            new_y = old_y
            self.update_position(agent, (new_x, new_y))
            self.print_matrix()

    def print_matrix(self):
        for row in self.matrix:
            print(" ".join([cell if cell is not None else "." for cell in row]))

    def get_matrix(self):
        return self.matrix

    def set_agents(self, agents):
        self.agents = agents
        self.agent_positions = {}
        self.agent_symbols = {}
        self.matrix = [[None for _ in range(self.width)] for _ in range(self.height)]

        self.initialize_agents()

def get_environment(width, height, focus_position, agents=None):
    return SimpleMultipleAgentEnvironment(width, height, focus_position, agents)
