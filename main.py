from simulation.iteration2.BasicSimulation import BasicSimulation
import environment.iteration2.LevelBuilder as LV
import agents.iteration1.Autoclicker as AC

agent_one = AC.get_agent(None, None, "A")
agent_two = AC.get_agent(None, None, "A")
agent_three = AC.get_agent(None, None, "A")
agent_four = AC.get_agent(None, None, "A")
agents = [agent_one, agent_two, agent_three, agent_four]
agents = ["A", "B", "C", "D"]
matrix = LV.build_level(3, 3, agents, 4, 10)
for row in matrix:
    print(row)

# Test two agents, which can change the visual stimuli for each other
#simulation = BasicSimulation(10, 2, (0, 2))
#simulation.run_simulation(steps=1)