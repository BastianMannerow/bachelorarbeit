import os
from iteration2 import DataVisualizer
from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame

###############################################################################
# HAUPT-SKRIPT
###############################################################################

import os
import concurrent.futures
from tqdm import tqdm
import multiprocessing
import time

# Angenommen, ClassicPublicGoodsGame ist bereits importiert oder definiert
# from your_module import ClassicPublicGoodsGame

def run_simulation(params):
    num_individuals, i, data_directory, end_after_rounds = params
    experiment_name = os.path.join(data_directory, f"{num_individuals}individuals{i + 1}")
    simulation = ClassicPublicGoodsGame((0, 2), end_after_rounds, experiment_name)
    simulation.run_simulation()
    return f"Completed: {experiment_name}"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    data_directory = os.path.join(os.getcwd(), "iteration2", "data")
    end_after_rounds = 50
    repetitions = 200

    # Sicherstellen, dass das Datenverzeichnis existiert
    os.makedirs(data_directory, exist_ok=True)

    # Vorbereitung der Aufgaben
    tasks = []
    for num_individuals in [4, 10, 50]:
        for i in range(repetitions):
            tasks.append((num_individuals, i, data_directory, end_after_rounds))

    # Anzahl der Prozesse festlegen (z.B. Anzahl der CPU-Kerne)
    num_workers = multiprocessing.cpu_count()

    # Fortschrittsbalken mit tqdm
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # map gibt die Ergebnisse in der Reihenfolge der Eingabe zurück
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulationen laufen"))

    # Optional: Alle abgeschlossenen Simulationen ausgeben
    # for result in results:
    #     print(result)

    print("Alle Simulationen sind abgeschlossen.")
    DataVisualizer.visualize_everything()