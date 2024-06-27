from simulation.AutoclickerRunner import AutoClickerRunner

# BasicMultipleAgents.run_simulation()
simulation = AutoClickerRunner(10, 2, (0, 2))
simulation.run_simulation(steps=1)