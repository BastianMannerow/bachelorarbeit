import pyactr as actr

class MatrixEnvironment(actr.Environment):
    def __init__(self, width, height, focus_position):
        super().__init__(focus_position=focus_position)
        self.width = width
        self.height = height
        self.matrix = [[None for _ in range(width)] for _ in range(height)]

    def update_position(self, agent, new_position):
        for row in self.matrix:
            for i in range(len(row)):
                if row[i] == agent:
                    row[i] = None
        self.matrix[new_position[1]][new_position[0]] = agent

    def print_matrix(self):
        for row in self.matrix:
            print(" ".join(["A" if cell is not None else "." for cell in row]))

    def get_matrix(self):
        return self.matrix
