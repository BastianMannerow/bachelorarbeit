import random
from collections import deque
from environment.iteration2.Food import Food
from environment.iteration2.Wall import Wall

def build_level(height, width, agents, food_amount, wall_density):
    # Calculate the total number of cells in the matrix
    total_cells = height * width
    # Calculate the number of walls based on wall_density
    wall_count = int(total_cells * (wall_density / 100))
    # Calculate the total number of objects to place
    total_objects = len(agents) + food_amount + wall_count

    # Check if there are more objects than available cells
    if total_objects > total_cells:
        raise ValueError("More objects than available cells in the matrix")

    # Initialize the matrix with None
    matrix = [[None for _ in range(width)] for _ in range(height)]

    # Function to get random empty position in the matrix
    def get_random_empty_position():
        while True:
            row = random.randint(0, height - 1)
            col = random.randint(0, width - 1)
            if matrix[row][col] is None:
                return row, col

    # Place agents
    for agent in agents:
        row, col = get_random_empty_position()
        matrix[row][col] = agent

    # Place food
    for _ in range(food_amount):
        row, col = get_random_empty_position()
        matrix[row][col] = Food()

    # Place walls
    for _ in range(wall_count):
        row, col = get_random_empty_position()
        matrix[row][col] = Wall()

    # Ensure all agents and food are accessible
    if not are_all_accessible(matrix, agents, height, width):
        raise ValueError("Not all agents and food are accessible")

    return matrix

def are_all_accessible(matrix, agents, height, width):
    def is_valid(r, c):
        return 0 <= r < height and 0 <= c < width and not isinstance(matrix[r][c], Wall)

    def bfs(start):
        visited = set()
        queue = deque([start])
        visited.add(start)
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if is_valid(nr, nc) and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return visited

    # Find all positions of agents and food
    positions = [(r, c) for r in range(height) for c in range(width)
                 if isinstance(matrix[r][c], (Food, type(agents[0])))]

    if not positions:
        return True

    # Check if all positions are connected
    accessible_positions = bfs(positions[0])
    return all(pos in accessible_positions for pos in positions)