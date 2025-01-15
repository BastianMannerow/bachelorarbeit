import os
from iteration2 import DataVisualizer
from iteration2.simulation.PublicGoodsGame import ClassicPublicGoodsGame
import concurrent.futures
from tqdm import tqdm
import multiprocessing


def run_simulation(params):
    """
    Initialises the simulation

    Args:
        params: simulations parameter
    Returns:
        experiment_name (String): return message
    """
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
    end_after_rounds = 25
    repetitions = 10

    # 80% CPU for parallelization
    num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))

    # A
    tasks = []
    experiment_type = "A"
    defector_amount = 0

    for num_individuals in [3, 6, 15]:
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
    
    # AP
    tasks = []
    experiment_type = "AP"
    defector_amount = 0
    for num_individuals in [3, 6, 15]:
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

    # B
    tasks = []
    experiment_type = "B"
    defector_amount = 1
    for num_individuals in [3, 6, 15]:
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

    # BP
    tasks = []
    experiment_type = "BP"
    defector_amount = 1
    for num_individuals in [3, 6, 15]:
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

    # C
    tasks = []
    experiment_type = "C"
    for num_individuals in [3, 6, 15]:
        defector_amount = num_individuals / 3
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

    # CP
    tasks = []
    experiment_type = "CP"
    for num_individuals in [3, 6, 15]:
        defector_amount = num_individuals / 3
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

    DataVisualizer.visualize_everything()
