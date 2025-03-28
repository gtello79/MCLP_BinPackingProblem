import random as rd
from base.baseline.bin import bin
from base.INSTACE_PARAM import MIN_BOXES_TO_POP, MAX_VOL_ACCEPT, TOLERANCE, N_TO_SWAP, DIFF_ACCEPT
import copy as cp
from base.Heuristics.BPP import BPP
from base.Heuristics.BSG import BSG


class MCLP(BSG):
    def __init__(self, ssh, L, W, H, id2box, verbose) -> None:
        self.ssh = ssh
        self.L = L
        self.W = W
        self.H = H
        self.id2box = id2box
        self.solution = []
        self.solution_size = 0
        self.verbose = verbose
        self.metrics = {}

    def generate_candidate_solution(
        self,
        boxes,
        r_param=1.0,
        bsg_time=1,
        extra_args="--greedy_only --min_fr=0.98",
    ) -> list:
        n_boxes = bin.get_nboxes(boxes)

        self.solution_size = 0
        self.solution = []
        n_supported_items = 0
        tot_support = 0.0

        # Generating candidate Solution
        while len(boxes) > 0:
            self.solution_size += 1
            vol_c = 0
            c = dict()
            # Llenado del contenedor
            while vol_c < r_param and len(boxes) != 0:
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
            remaining, loaded, json_data = self.bsg_solve(
                boxes=c,
                bsg_time=bsg_time,
                args=extra_args,
            )
            utilization = json_data["utilization"]
            support = json_data["tot_support"]
            full_supported_items = json_data["full_supported_items"]

            tot_support += support
            n_supported_items += full_supported_items

            if self.verbose:
                print(utilization, end=" ")

            layout = json_data.get("layout", None)

            container = bin(self.solution_size, loaded, utilization, layout)
            # Se agrega la solucion
            self.solution.append(container)

            # añadiendo las restantes para ser distribuidas nuevamente
            for key in remaining:
                if key in boxes:
                    boxes[key] += remaining[key]
                else:
                    boxes[key] = remaining[key]

        av_support = tot_support / n_boxes
        supported_items = n_supported_items / n_boxes

        if self.verbose:
            print(
                f"Initial Solution: {len(self.solution)} av_support: {
                    av_support} supported_items: {supported_items}"
            )

        # Saving metrics
        self.metrics['solution_size'] = len(self.solution)
        self.metrics['supported_items'] = supported_items
        self.metrics['av_support'] = av_support

        return self.solution

    def random_swaps(self,
                     best_solution,
                     max_iter=100000,
                     extra_args="",
                     lb=1,
                     max_no_improvements=50,
                     bsg_time=5
                     ):

        no_improvements = 0

        for i in range(max_iter):
            solution = cp.deepcopy(best_solution)

            # Realize the Swap Process over the current solution
            diff_var = BPP._swap(
                solution=solution, n=N_TO_SWAP, max_vol_accept=MAX_VOL_ACCEPT, tolerance=TOLERANCE)

            # Evaluate de variation over 1e-7
            if diff_var > DIFF_ACCEPT:

                # Verify the factibility in the solution
                verified_solution_flag = self.verify_solution(
                    solution=solution,
                    bsg_time=bsg_time,
                    args=extra_args,
                )

                if verified_solution_flag:

                    if self.verbose:
                        print("A new solution verificated")
                        print(f"Current {len(best_solution)
                                         } -> New {len(solution)}")

                    no_improvements = 0
                    best_solution = []
                    for b in solution:
                        b.calculate_vol()
                        if b.vol > 1e-5:
                            best_solution.append(cp.deepcopy(b))

                else:
                    no_improvements += 1
            
            print(f"Iter {i}: Current {len(best_solution)} -> New {len(solution)}")

            if no_improvements > max_no_improvements or len(best_solution) == lb:
                break

        # Update Metrics
        self.metrics['solution_size'] = len(self.solution)
        self.solution = best_solution

        return best_solution

    def verify_solution(
        self,
        solution: list,
        bsg_time=5,
        args="",
    ) -> bool:

        for s in solution:
            boxes = s.boxes

            # Verification de bin objetivos
            if not (s.verify):
                if not boxes:
                    # Omite los bins que no tienen cajas
                    if self.verbose:
                        print(f"Empty bin: {boxes} -> {s.vol}")
                    continue
                else:
                    remaining, _, s.utilization = self.bsg_solve(
                        boxes=boxes,
                        bsg_time=bsg_time,
                        args=args,
                    )

                    correct_solution = len(remaining) == 0

                    if correct_solution:
                        s.verify = correct_solution
                    else:
                        return correct_solution

            # If the solution was verificated
            else:
                continue

        # Actualiza la solución con los bins encontrados
        solution = [s for s in solution if s.verify]

        return True
