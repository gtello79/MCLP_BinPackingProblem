import random as rd
from base.Heuristics.bsg import bsg_solve
from base.baseline.bin import bin
from base.INSTACE_PARAM import MIN_BOXES_TO_POP


class MCLP:
    def __init__(self, ssh, L, W, H, id2box, verbose) -> None:
        self.ssh = ssh
        self.L = L
        self.W = W
        self.H = H
        self.id2box = id2box
        self.solution = []
        self.solution_size = 0
        self.verbose = verbose

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

            remaining, loaded, json_data = bsg_solve(
                self.ssh,
                self.L,
                self.W,
                self.H,
                c,
                self.id2box,
                time=bsg_time,
                args=extra_args,
                verbose=False,
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
                f"Initial Solution: {len(self.solution)} av_support: {av_support} supported_items: {supported_items}"
            )

        return self.solution

    def verify_solution(
        self,
        solution: list,
        id2box,
        bsg_time=5,
        args="",
    ) -> bool:
        factibility = True

        for s in solution:
            if not (s.verify):
                boxes = s.boxes
                persistens = True
                while persistens:
                    try:

                        remaining, _, s.utilization = bsg_solve(
                            self.ssh,
                            self.L,
                            self.W,
                            self.H,
                            boxes,
                            id2box,
                            time=bsg_time,
                            args=args,
                            verbose=self.verbose,
                        )
                        persistens = False
                    except Exception as e:
                        persistens = True

                if len(remaining) != 0:
                    return False
                else:
                    s.verify = True
        return factibility