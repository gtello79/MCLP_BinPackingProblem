from base.Heuristics.mclp import generate_candidate_solution, random_swaps
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
    host,
    port,
    username,
    password,
    min_bin,
    VERBOSE,
)

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
#MAX_ITER = params_args.MAX_ITER
instances_name = params_args.instance
## Tiempo de BSG
bsg_time = params_args.bsg_time
## Parametro de llenado del contenedor
r_param = params_args.r_param
n_runs = params_args.n_runs
max_no_improvements = params_args.max_no_improvements

# Define extra args
extra_args = f"--max_bl={max_bl} --min_fr={min_fr} --bottom_up --show_layout"
if bsg_time == 0:
    extra_args += " --greedy_only"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

dataloader = DatasetLoader(instances_name)
instance_files = dataloader.instances_list

filename_list = []
results = []
best_sols = []
times_list = []
min_list = []
for filename in instance_files:
    sols = []
    best_sols = []
    times = []

    tot_bins = 0
    min_bins = min_bin
    start = timeit.default_timer()
    # Load instance info
    L, W, H, _boxes, id2box = dataloader.get_instance(filename=filename)
    total_vol = bin.get_vol_by_boxes_group(_boxes)
    lb = math.ceil(total_vol)

    # Running experiments
    for k in range(n_runs):
        boxes = _boxes.copy()
        best_solution = generate_candidate_solution(
            ssh,
            L,
            W,
            H,
            boxes,
            id2box,
            r_param=r_param,
            bsg_time=bsg_time,
            extra_args=extra_args,
            verbose=VERBOSE,
        )

        if swaps == "--swaps":
            best_solution = random_swaps(
                ssh,
                L,
                W,
                H,
                id2box,
                best_solution,
                max_iter=MAX_ITER,
                extra_args=extra_args,
                max_no_improvements=max_no_improvements,
                lb=lb,
            )
        tot_bins += len(best_solution)

        if len(best_solution) < min_bins:
            min_bins = len(best_solution)

    stop = timeit.default_timer()
    sols.append(tot_bins / n_runs)
    best_sols.append(min_bins)
    times.append(stop - start)

    print(filename, ":", min(sols), mean(sols), mean(best_sols), mean(times))

    filename_list.append(filename)
    results.append(mean(sols))
    best_sols.append(mean(best_sols))
    times_list.append(mean(times))
    min_list.append(min(sols))


csv_file = "results.csv"
print(len(filename_list), len(results), len(best_sols), len(times_list), len(min_list))

df = DataFrame(
    {
        "filename": filename_list,
        "min_bins": min_list,
        "results": results,
        "best_sols": best_sols,
        "times": times_list,
    }
)
df.to_csv(csv_file, index=False)
