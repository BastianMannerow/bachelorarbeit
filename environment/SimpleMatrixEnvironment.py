
import customPyACTR as actr

class SimpleMatrixEnvironment(actr.Environment):
    def __init__(self, width, height, focus_position):
        super().__init__(focus_position=focus_position)
        self.width = width
        self.height = height
        self.matrix = [[None for _ in range(width)] for _ in range(height)]
        self.agent_position = (0, 0)  # Initial position of the agent
        self.matrix[0][0] = 'A'  # Code for the Agent

    def update_position(self, new_position):
        old_x, old_y = self.agent_position
        new_x, new_y = new_position

        # Ckecks if the position is within its boundaries
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.matrix[old_y][old_x] = None
            self.matrix[new_y][new_x] = 'A'
            self.agent_position = new_position

    def move_agent_right(self, symbol):
        old_x, old_y = self.agent_position
        new_x = old_x + 1
        new_y = old_y
        self.update_position((new_x, new_y))
        self.print_matrix()

    def print_matrix(self):
        for row in self.matrix:
            print(" ".join(["A" if cell is not None else "." for cell in row]))

    def get_matrix(self):
        return self.matrix

def get_environment(width, height, focus_position):
    return SimpleMatrixEnvironment(width, height, focus_position)