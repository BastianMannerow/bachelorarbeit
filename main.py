from simulation.iteration1.SingleRunnerInMatrix import SimpleAutoclickerRunner
from simulation.iteration1.VisualStimulusLocator import SimpleVisualLocator
from simulation.iteration1.SimpleTwoAutoclickers import SimpleTwoAutoclickers
from simulation.iteration1.SimpleDifferentAgentStepper import DifferentAgentStepper
from simulation.iteration1.RoundBasedRunning import RoundBasedRunning
from simulation.iteration1.ChangeVisualStimuli import ChangeVisualStimuli
from simulation.iteration1.SimpleTutorial import TestAgents

# BasicMultipleAgents.run_simulation()

# Test an input to the environment
#simulation = SimpleAutoclickerRunner(10, 2, (0, 2))
#simulation.run_simulation(steps=1)

# Test to find visual stimuli
# simulation = SimpleVisualLocator(15, 4, (200, 200))
# simulation.run_simulation(steps=1)

# Test two agents, which move in the same environment
#simulation = SimpleTwoAutoclickers(10, 2, (0, 2))
#simulation.run_simulation(steps=1)

# Test two agents, which have different logging statements
# simulation = DifferentAgentStepper(10, 2, (0, 2))
# simulation.run_simulation(steps=1)

# Test two agents, which move in the same environment, but round based
# simulation = RoundBasedRunning(10, 2, (0, 2))
# simulation.run_simulation(steps=1)

# Test two agents, which can change the visual stimuli for each other
simulation = ChangeVisualStimuli(10, 2, (0, 2))
simulation.run_simulation(steps=1)

#simulation = TestAgents()
#simulation.run_simulation()