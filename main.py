import os
from iteration2 import DataVisualizer
from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame
import concurrent.futures
from tqdm import tqdm
import multiprocessing

def run_simulation(params):
    experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment = params
    simulation = ClassicPublicGoodsGame((0, 2), end_after_rounds, experiment_name, num_individuals, defector_amount, multiplication_factor, allow_punishment)
    simulation.run_simulation()
    return f"Completed: {experiment_name}"

if __name__ == "__main__":
    data_directory = os.path.join(os.getcwd(), "iteration2", "data")
    os.makedirs(data_directory, exist_ok=True)

    # Configuration
    end_after_rounds = 25
    repetitions = 10
    tasks = []

    # A = 0 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = 0
        experiment_type = "A"
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()

    # AP = 0 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = 0
        experiment_type = "A"
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()

    # B = 1 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = 1
        experiment_type = "B"
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()

    # BP = 1 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = 1
        experiment_type = "B"
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()

    # C = 1/3 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = num_individuals / 3
        experiment_type = "C"
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()

    # CP = 0 Defectors
    for num_individuals in [3, 6, 15]:
        defector_amount = num_individuals / 3
        experiment_type = "C"
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount, multiplication_factor, allow_punishment))
            # 2

            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 1/2
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}{num_individuals}individuals{i + 1}")
            multiplication_factor = (num_individuals + defector_amount) * 3/4
            tasks.append((experiment_name, num_individuals, i, data_directory, end_after_rounds, defector_amount,
                          multiplication_factor, allow_punishment))
    # Parallelization with 80% CPU usage
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
    # Updates
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks), desc="Simulation running..."))

    print("Simulation finished successfully.")
    DataVisualizer.visualize_everything()
