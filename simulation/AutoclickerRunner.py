from agents import Autoclicker
from environment import SimpleMatrixEnvironment

def run_simulation():
    # Matrixgröße definieren
    MATRIX_WIDTH = 10
    MATRIX_HEIGHT = 5

    # Environment erstellen
    environment = SimpleMatrixEnvironment.get_environment(MATRIX_WIDTH, MATRIX_HEIGHT, focus_position=(0, 2))
    environment.print_matrix()  # Just to visualize the initial matrix state
    agent = Autoclicker.get_agent(None)
    simulation_agent = agent.simulation(realtime=True, environment_process=environment.environment_process)
    simulation_agent.run(1)