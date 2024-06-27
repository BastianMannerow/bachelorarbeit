from simulation.SimpleAutoclickerRunner import SimpleAutoclickerRunner
from simulation.SimpleVisualLocator import SimpleVisualLocator
from simulation.SimpleTwoAutoclickers import SimpleTwoAutoclickers

# BasicMultipleAgents.run_simulation()

# Test an input to the environment
#simulation = SimpleAutoclickerRunner(10, 2, (0, 2))
#simulation.run_simulation(steps=1)

# Test to find visual stimuli
#simulation = SimpleVisualLocator(15, 4, (200, 200))
#simulation.run_simulation(steps=1)

# Test two agents, which move in the same environment
simulation = SimpleTwoAutoclickers(10, 2, (0, 2))
simulation.run_simulation(steps=1)