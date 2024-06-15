from agents import test
from agents import test2
from agents import test3
from agents import test4
from agents import test5
import string
import random
import time
import pyactr as actr

from environment.TestEnvironment import MatrixEnvironment

"""
agent = test.getAdditionAgent()
agent2 = test2.getAdditionAgent()

# Start the first agent's simulation and run it
x = agent.simulation()
x.run()

print("------------------------------------------------")

# Start the second agent's simulation and run it
y = agent2.simulation()
y.run()
"""
print("------------------------------------------------")
"""
# Stimulus generieren
stimulus = random.sample(string.ascii_uppercase, 1)[0]
text = {1: {'text': stimulus, 'position': (100,100)}}

# Environment erstellen
environ = actr.Environment(focus_position=(100,100))

# Beide Agenten initialisieren
m = test3.pressKey(environ)
n = test3.pressKey(environ)

# Simulation für beide Agenten erstellen
sim_m = m.simulation(realtime=True, environment_process=environ.environment_process, stimuli=text, triggers=stimulus, times=1)
sim_n = n.simulation(realtime=True, environment_process=environ.environment_process, stimuli=text, triggers=stimulus, times=1)

# Beide Simulationen gleichzeitig ausführen
sim_m.run(1)
sim_n.run(1)
print("------------------------------------------------")
"""

# Matrixgröße definieren
MATRIX_WIDTH = 10
MATRIX_HEIGHT = 5

# Environment erstellen
environ = MatrixEnvironment(MATRIX_WIDTH, MATRIX_HEIGHT, focus_position=(0, 2))

# Beide Agenten initialisieren
m = test4.pressKey(environ)
n = test5.pressKey(environ)

# Startpositionen der Agenten
start_positions = [(0, 2), (0, 3)]
environ.update_position(m, start_positions[0])
environ.update_position(n, start_positions[1])

# Simulation für beide Agenten erstellen
sim_m = m.simulation(realtime=True, environment_process=environ.environment_process)
sim_n = n.simulation(realtime=True, environment_process=environ.environment_process)

# Funktion zum Bewegen der Agenten
def move_agent(agent, position, key):
    if key == 'w':
        new_position = (position[0] + 1, position[1])
        if new_position[0] < MATRIX_WIDTH:
            environ.update_position(agent, new_position)
            return new_position
    return position

# Beide Simulationen ausführen und die Bewegung der Agenten verfolgen
positions = {m: start_positions[0], n: start_positions[1]}
for _ in range(MATRIX_WIDTH):
    # Simulationen laufen lassen
    sim_m.run(1)
    sim_n.run(1)

    # Agenten bewegen
    positions[m] = move_agent(m, positions[m], 'w')
    positions[n] = move_agent(n, positions[n], 's')

    # Matrix drucken
    environ.print_matrix()

    # Pause von einer Sekunde
    time.sleep(1)

    # Überprüfen, ob ein Agent das Ende erreicht hat
    if positions[m][0] == MATRIX_WIDTH - 1 or positions[n][0] == MATRIX_WIDTH - 1:
        break

# Gewinner bestimmen
if positions[m][0] == MATRIX_WIDTH - 1:
    print("Agent m hat gewonnen!")
elif positions[n][0] == MATRIX_WIDTH - 1:
    print("Agent n hat gewonnen!")
else:
    print("Kein Agent hat das Ende erreicht.")