import random as rd
from base.tools.utils import get_random_bin
import timeit
from base.baseline.bin import bin

seed_t = int(timeit.default_timer())
rd.seed(seed_t)

class BPP():

    def calculate_variance(bin_1, bin_2):
        iniA = bin_1.vol
        iniB = bin_2.vol
        var_ini = (iniA - 1.0) ** 2 + (iniB - 1.0) ** 2

        return var_ini

    @classmethod
    def _swap(cls, solution, n=2, max_vol_accept=1.0, tolerance=0.1):
        r = tolerance * rd.random()
        nA = rd.randint(1, n)
        nB = rd.randint(0, n)
        
        # Choise two bins for swap boxes
        bin_A = get_random_bin(solution_list=solution)
        bin_B = get_random_bin(solution_list=solution, b=bin_A)
        
        # Calculate the initial volume
        var_ini = cls.calculate_variance(bin_A, bin_B)

        # Get the total boxes to swap
        boxes_A = bin_A.pop_random_boxes(nA)
        boxes_B = bin_B.pop_random_boxes(nB)

        adjvolA = bin.get_vol_by_boxes_group(boxes_A)
        adjvolB = bin.get_vol_by_boxes_group(boxes_B)

        condition_1 = adjvolA > adjvolB and bin_B.vol + adjvolA <= max_vol_accept + r
        condition_2 = adjvolB > adjvolA and bin_A.vol + adjvolB <= max_vol_accept + r

        # Verify the factibility to swap boxes
        if condition_1 or condition_2:
            bin_A.insert_boxes(boxes_B)
            bin_B.insert_boxes(boxes_A)
            print(f"Swap {len(boxes_A)} boxes from bin {bin_A.id} to bin {bin_B.id}")
        else:
            bin_A.insert_boxes(boxes_A)
            bin_B.insert_boxes(boxes_B)

        # Calculate the new volume in each bin
        bin_A.calculate_vol()
        bin_B.calculate_vol()

        var_final = cls.calculate_variance(bin_A, bin_B)
        var_diff = var_final - var_ini

        return var_diff if condition_1 or condition_2 else -10