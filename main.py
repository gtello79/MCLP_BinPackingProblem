from base.Heuristics.MCLP import MCLP
from base.baseline.bin import bin
from base.Heuristics.dataset import DatasetLoader
from base.INSTACE_PARAM import (
    min_fr,
    max_bl,
    MAX_ITER,
    instances_name,
    bsg_time,
    r_param,
    max_no_improvements,
    swaps,
    n_runs,
    min_bin,
    VERBOSE,
    LOCAL_EXECUTION
)

from PassCredentials import username, password, host, port
from statistics import mean
from argparse import ArgumentParser
import math
import paramiko
import timeit
from pandas import DataFrame


def parse_arguments():
    parser = ArgumentParser(description="Bin Packing Problem")

    parser.add_argument(
        "--instance", type=str, default=instances_name, help="Instance name"
    )
    parser.add_argument("--bsg_time", type=int, default=bsg_time, help="Time for BSG")
    parser.add_argument(
        "--r_param",
        type=float,
        default=r_param,
        help="Parameter for filling the container",
    )
    parser.add_argument("--n_runs", type=int, default=n_runs, help="Number of runs")
    parser.add_argument("--swaps", type=str, default="--swaps", help="Swaps")
    parser.add_argument(
        "--max_no_improvements",
        type=int,
        default=max_no_improvements,
        help="Max no improvements",
    )
    parser.add_argument("--min_fr", type=float, default=min_fr, help="Min filled ratio")
    parser.add_argument("--max_bl", type=int, default=max_bl, help="Max blocks")
    parser.add_argument("--MAX_ITER", type=int, default=MAX_ITER, help="Max iterations")
    parser.add_argument("--MIN_BOXES_TO_POP", type=int, help="Min boxes to pop")

    return parser.parse_args()


params_args = parse_arguments()

# Algorithm settings
# Minimo porcentaje ocupado para considerar la generación de un bloque
min_fr = params_args.min_fr
# maxima cantidad de bloques a generar por bsg
max_bl = params_args.max_bl
# MAX_ITER = params_args.MAX_ITER
instances_name = params_args.instance
## Tiempo de BSG
bsg_time = params_args.bsg_time
## Parametro de llenado del contenedor
r_param = params_args.r_param
n_runs = params_args.n_runs
max_no_improvements = params_args.max_no_improvements

# Define extra args
extra_args = f"--max_bl={max_bl} --min_fr={min_fr} --show_layout"
if bsg_time == 0:
    extra_args += " --greedy_only"

# Make connection with the server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

dataloader = DatasetLoader(instances_name)
instance_files = dataloader.instances_list


# Imprime todos los parametros que son importados
print(f"Instances: {instances_name} - Execution on Local?: {LOCAL_EXECUTION}")
print(
    f"min_fr={min_fr}, max_bl={max_bl}, bsg_time={bsg_time}, r_param={r_param}, n_runs={n_runs}, max_no_improvements={max_no_improvements}"
)
print(f"Extra args: {extra_args}")

filename_list = []
results = []
best_sols_list = []
times_list = []
min_list = []

data = []
try:
    for filename in instance_files:
        
        times = []

        sols = []
        best_sols = []

        tot_bins = 0
        min_bins = min_bin

        # Load instance info
        L, W, H, _boxes, id2box = dataloader.get_instance(filename=filename)

        total_vol = bin.get_vol_by_boxes_group(_boxes)
        lb = math.ceil(total_vol)

        mclp_instance = MCLP(ssh,L,W,H,id2box,VERBOSE)


        # Running experiments
        for k in range(n_runs):
            start_time = timeit.default_timer()
            boxes = _boxes.copy()

            # Generate initial solution(
            best_solution = mclp_instance.generate_candidate_solution(boxes, r_param, bsg_time, extra_args)

            # Aplication Swaps sobre una solucion mejor que la propuesta
            if swaps == "--swaps" and len(best_solution) != lb:
                best_solution = mclp_instance.random_swaps(
                    best_solution=best_solution,
                    max_iter=MAX_ITER,
                    extra_args=extra_args,
                    lb=lb,
                    max_no_improvements=max_no_improvements,
                    bsg_time=bsg_time
                )

            else:
                if len(best_solution) == lb:
                    print("The algorithm gots lower bound on the Generate candidate solution")
            tot_bins += len(best_solution)

            # Store the min solution of the run
            if len(best_solution) < min_bins:
                min_bins = len(best_solution)

            resolution_time = timeit.default_timer() - start_time

            # Store results
            times.append(resolution_time)

        sols.append(tot_bins / n_runs)
        best_sols.append(min_bins)

        print(filename, ":", mean(best_sols), mean(sols), min(sols), mean(times))
        current_info = (filename[0], filename[1], mean(best_sols), mean(sols), min(sols), mean(times))

        data.append(current_info)

        # Present information for the DataFrame
        filename_list.append(filename[0])
        results.append(mean(sols))
        best_sols_list.append(mean(best_sols))
        times_list.append(mean(times))
        min_list.append(min(sols))


except Exception as e:
    print(e.with_traceback())
    import pdb

    pdb.set_trace()

current_time = timeit.default_timer()
if instances_name == 'martello':
    print(f'Creating results for {instances_name} with r_param {r_param} at {current_time}')
    # Crear DataFrame
    df = DataFrame(data, columns=["file", "instance", "best_solution", "average", "min_sol", "execution_time"])

    # Crear DataFrame
    csv_file = f"base/Results/InicialSolution/{instances_name}/results_{r_param}_{current_time}.csv"
    df.to_csv(csv_file, index=False)

    # Agrupar por clase y calcular promedios
    df = df.drop(columns=["instance"])
    grouped_df = df.groupby("file").mean()

    print(grouped_df)

    # Crear DataFrame Consolidated
    csv_file = f"base/Results/InicialSolution/{instances_name}/Consolidatedresults_{r_param}_{current_time}.csv"
    grouped_df.to_csv(csv_file, index=True)

