import os
from iteration2 import DataVisualizer
from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame
import concurrent.futures
from tqdm import tqdm
import multiprocessing


def run_simulation(params):
    (
        experiment_name,
        num_individuals,
        i,
        data_directory,
        end_after_rounds,
        defector_amount,
        multiplication_factor,
        allow_punishment,
    ) = params

    # Falls defector_amount ein Bruch ist, sicherstellen, dass int() erwartet wird:
    # defector_amount = int(defector_amount)

    simulation = ClassicPublicGoodsGame(
        (0, 2),
        end_after_rounds,
        experiment_name,
        int(num_individuals),
        int(defector_amount),
        multiplication_factor,
        allow_punishment
    )
    simulation.run_simulation()
    return f"Completed: {experiment_name}"


if __name__ == "__main__":
    data_directory = os.path.join(os.getcwd(), "iteration2", "data")
    os.makedirs(data_directory, exist_ok=True)

    # Konfiguration
    end_after_rounds = 25
    repetitions = 1

    # Wir wählen für die Parallelisierung 80 % der verfügbaren CPUs
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))

    # =========================
    # Block A = 0 Defectors
    # =========================
    tasks = []
    experiment_type = "A"
    defector_amount = 0
    """
    for num_individuals in [15, 21]:
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (A=0 Defectors)"))
    print("Simulation finished successfully (Block A).")
    
    # =========================
    # Block AP = 0 Defectors
    # =========================
    tasks = []
    experiment_type = "AP"
    defector_amount = 0
    for num_individuals in [15, 21]:
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (AP=0 Defectors)"))
    print("Simulation finished successfully (Block AP).")

    # =========================
    # Block B = 1 Defector
    # =========================
    tasks = []
    experiment_type = "B"
    defector_amount = 1
    for num_individuals in [15, 21]:
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (B=1 Defector)"))
    print("Simulation finished successfully (Block B).")

    # =========================
    # Block BP = 1 Defector
    # =========================
    tasks = []
    experiment_type = "BP"
    defector_amount = 1
    for num_individuals in [15, 21]:
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (BP=1 Defector)"))
    print("Simulation finished successfully (Block BP).")

    # =========================
    # Block C = 1/3 Defectors
    # =========================
    tasks = []
    experiment_type = "C"
    for num_individuals in [15, 21]:
        defector_amount = num_individuals / 3  # ggf. int(num_individuals / 3)
        for i in range(repetitions):
            allow_punishment = False
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (C=1/3 Defectors)"))
    print("Simulation finished successfully (Block C).")

    # =========================
    # Block CP = 1/3 Defectors
    # =========================
    tasks = []
    experiment_type = "CP"
    for num_individuals in [15, 21]:
        defector_amount = num_individuals / 3  # ggf. int(num_individuals / 3)
        for i in range(repetitions):
            allow_punishment = True
            # 1
            experiment_name = os.path.join(data_directory, f"{experiment_type}a{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 2
            experiment_name = os.path.join(data_directory, f"{experiment_type}b{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 1 / 2
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )
            # 3
            experiment_name = os.path.join(data_directory, f"{experiment_type}c{num_individuals}individuals{i + 1}")
            multiplication_factor = num_individuals * 3 / 4
            tasks.append(
                (
                    experiment_name,
                    num_individuals,
                    i,
                    data_directory,
                    end_after_rounds,
                    defector_amount,
                    multiplication_factor,
                    allow_punishment,
                )
            )

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(tqdm(executor.map(run_simulation, tasks), total=len(tasks),
                            desc="Simulation running (CP=1/3 Defectors)"))
    print("Simulation finished successfully (Block CP).")
    """
    DataVisualizer.visualize_everything()
