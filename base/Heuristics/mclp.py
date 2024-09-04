import random as rd
from base.Heuristics.bsg import bsg_solve
from base.baseline.bin import bin
from base.INSTACE_PARAM import MIN_BOXES_TO_POP
import copy as cp

def generate_candidate_solution(
    ssh,
    L,
    W,
    H,
    boxes,
    id2box,
    r_param=1.0,
    bsg_time=1,
    extra_args="--greedy_only --min_fr=0.98",
    verbose=False,
) -> list:

    n_boxes = bin.get_nboxes(boxes)
    # Identificador de bin
    solution_id = 1
    solution = []
    n_supported_items = 0
    tot_support = 0.0

    # Generating candidate Solution
    while len(boxes) > 0:
        
        vol_c = 0
        c = dict()

        # Llenado del contenedor hasta que se cumpla el parametro
        while (vol_c < r_param and len(boxes) != 0):
            boxes_keys = list(boxes.keys())
            r = rd.randint(0, len(boxes_keys) - 1)

            b = boxes_keys[r]
            n = min(boxes[b], MIN_BOXES_TO_POP)
            boxes[b] = boxes[b] - n

            # No quedan mas cajas del tipo b
            if boxes[b] == 0:
                boxes.pop(b)

            # Si no se ha agregado el tipo de caja
            if b not in c:
                c[b] = 0

            # Agregar cantidad de cajas
            c[b] = c[b] + n

            vol_box = b.vol
            vol_c = vol_c + vol_box * n

        # Evaluar contenedor cajas obtenidas
        remaining, loaded, json_data = bsg_solve(
            ssh, L, W, H, c, id2box, time=bsg_time, args=extra_args, verbose=False
        )

        utilization = json_data["utilization"]
        support = json_data["tot_support"]
        full_supported_items = json_data["full_supported_items"]

        tot_support += support
        n_supported_items += full_supported_items
        if verbose:
            print(utilization, end=" ")

        layout = json_data.get("layout", None)

        container = bin(solution_id, loaded, utilization, layout)
        
        # Se agrega la solucion
        solution.append(container)

        # añadiendo las restantes para ser distribuidas nuevamente
        for key in remaining:
            if key in boxes:
                boxes[key] += remaining[key]
            else:
                boxes[key] = remaining[key]

        solution_id += 1

#    import pdb; pdb.set_trace()
    
    av_support = tot_support / n_boxes
    supported_items = n_supported_items / n_boxes


    if verbose:
        print(
            f"Initial Solution: {len(solution)} av_support: {av_support} supported_items: {supported_items}"
        )

    return solution


# Retorna la probabilidad de llenar el bin
def calculate_prob(solution: list, metric: float) -> float:
    counter = 0
    size = 0
    for s in solution:
        if len(s.boxes) != 0:
            size += 1
            v = bin.get_vol_by_boxes_group(s.boxes)
            if v > metric:
                counter += 1
    prob_calculate = (float)(counter / size)
    return prob_calculate


def get_random_bin(solution_list: list, b: bin = None) -> bin:
    index_bin = rd.randint(0, len(solution_list) - 1)
    bin_selected = solution_list[index_bin]

    # Se retorna un bin distinto al seleccionado y que no este vacio
    while b == bin_selected or len(bin_selected.boxes) == 0:

        index_bin = int(rd.randint(0, len(solution_list) - 1))
        bin_selected = solution_list[index_bin]

    return bin_selected


def eval_list_bins(solution: list, media) -> float:
    quality = 0.0

    for b in solution:
        bin_boxes = b.boxes
        diff = bin.get_vol_by_boxes_group(bin_boxes) - media
        quality += pow(diff, 2)

    return quality


def verify_solution(
    ssh,
    L: int,
    W: int,
    H: int,
    solution: list,
    id2box,
    bsg_time=5,
    args="",
    verbose=False,
) -> bool:
    factibility = True
    for s in solution:
        if not (s.verify):
            boxes = s.boxes

            persistens = True
            while persistens:
                try:
                    final = bsg_solve(
                        ssh,
                        L,
                        W,
                        H,
                        boxes,
                        id2box,
                        time=bsg_time,
                        args=args,
                        verbose=verbose,
                    )
                    remaining, _, s.utilization = final
                    persistens = False
                except Exception as e:
                    persistens = True
                    raise(e)

            if len(remaining) != 0:
                return False
            else:
                s.verify = True
    return factibility


def swap(solution, n=2, max_vol_accept=1.0, tolerance=0.1):
    
    r = tolerance * rd.random()
    nA = rd.randint(1, n)
    nB = rd.randint(0, n)
    
    # Se escogen dos bin
    bin_A = get_random_bin(solution_list=solution)
    bin_B = get_random_bin(solution_list=solution, b=bin_A)

    iniA = bin_A.vol
    iniB = bin_B.vol
    var_ini = (iniA - 1.0) ** 2 + (iniB - 1.0) ** 2

    boxes_A = bin_A.pop_random_boxes(nA)
    boxes_B = bin_B.pop_random_boxes(nB)

    adjvolA = bin.get_vol_by_boxes_group(boxes_A)
    adjvolB = bin.get_vol_by_boxes_group(boxes_B)

    condition_1 = adjvolA > adjvolB and iniB + adjvolA <= max_vol_accept + r
    condition_2 = adjvolB > adjvolA and iniA + adjvolB <= max_vol_accept + r

    if condition_1 or condition_2:
        bin_A.insert_boxes(boxes_B)
        bin_B.insert_boxes(boxes_A)

    else:
        bin_A.insert_boxes(boxes_A)
        bin_B.insert_boxes(boxes_B)


    bin_A.calculate_vol()
    bin_B.calculate_vol()

    iniA = bin_A.vol
    iniB = bin_B.vol
    var_final = (iniA - 1.0) ** 2 + (iniB - 1.0) ** 2
    var_diff = var_final - var_ini

    return var_diff if condition_1 or condition_2 else -10


def random_swaps(
    ssh,
    L,
    W,
    H,
    id2box,
    best_solution,
    max_iter=100000,
    extra_args="",
    lb=1,
    max_no_improvements=50,
):
    if len(best_solution) == lb:
        return best_solution

    no_improvements = 0
    for i in range(max_iter):
        solution = cp.deepcopy(best_solution)
        diff_var = swap(
            solution, n=2, max_vol_accept=0.65, tolerance=0.3)
        print(i, diff_var, len(solution))
        
        if diff_var > 1e-7:
            print('Verify solution')
            verified_solution = verify_solution(
                ssh,
                L,
                W,
                H,
                solution,
                id2box,
                bsg_time=5,
                args=extra_args,
                verbose=False,
            )

            if verified_solution:
                no_improvements = 0
                best_solution = []
                for b in solution:
                    b.calculate_vol()
                    if b.vol > 1e-5:
                        best_solution.append(cp.deepcopy(b))

            else:
                no_improvements += 1

        if no_improvements > max_no_improvements or len(best_solution) == lb:
            break

    return best_solution
