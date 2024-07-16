import paramiko

import random as rd
from base.Heuristics.mclp import get_random_bin, verify_solution
from base.Heuristics.bsg import bsg_solve
from base.Heuristics.dataset import DatasetLoader
from statistics import mean

from base.baseline.bin import bin

import sys
import copy as cp
import math
import timeit

host = "158.251.88.197"
port = 22
username = "iaraya"
password = "lunyta22"

r_param = 4.0                 # Parametro de llenado del contenedor
min_fr = 0.99               # minimo porcentaje ocupado para considerar la generación de un bloque
max_bl = 10000           # maxima cantidad de bloques a generar por bsg
bsg_time = 5               # Tiempo de BSG
max_no_improvements = 50
MAX_ITER = 100000
extra_args = f'--max_bl={max_bl} --min_fr={min_fr} --bottom_up --show_layout'

instances_name = sys.argv[1]
bsg_time = int(sys.argv[2])
r_param = float(sys.argv[3])
n_runs = int(sys.argv[4])
swaps = sys.argv[5]
max_no_improvements = int(sys.argv[6])
if bsg_time==0: 
    extra_args+= ' --greedy_only'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password)

dataloader = DatasetLoader(instances_name)
def get_adjusted_vol(boxes):
    vol=0.0
    for box in boxes:
        vol += box.vol*boxes[box]
    return vol

def get_nboxes(boxes):
    n=0
    for box in boxes:
        n += boxes[box]
    return n

def get_vol(boxes):
    vol=0.0
    for box in boxes:
        vol += box.vol*boxes[box]
    return vol

def adjusted_swap(solution, n=2,  max_vol_accept=1.0, tolerance=0.1, verbose=True):

    bin_A = get_random_bin(s = solution)
    bin_B = get_random_bin(s = solution, b = bin_A)

    iniA = bin_A.vol
    iniB = bin_B.vol

    var_ini = (iniA-1.0)**2 + (iniB -1.0)**2

    nA = rd.randint(1, n)
    boxes_A = bin_A.pop_random_boxes(nA)
    adjvolA = get_adjusted_vol(boxes_A)

    nB = rd.randint(0, n)
    boxes_B = bin_B.pop_random_boxes(nB)
    adjvolB = get_adjusted_vol(boxes_B)

    r = tolerance*rd.random()

    condition_1 = adjvolA > adjvolB and iniB + adjvolA <= max_vol_accept + r
    condition_2 = adjvolB > adjvolA and iniA + adjvolB <= max_vol_accept + r

    if condition_1 or condition_2:
        bin_A.insert_boxes(boxes_B)
        bin_B.insert_boxes(boxes_A)
    else: 
        return -10

    iniA = bin_A.vol
    iniB = bin_B.vol

    var_final = (iniA-1.0)**2 + (iniB-1.0)**2
    var_diff = var_final - var_ini

    return var_diff

def get_sorted_vols(solution):
    volumens = []
    acum_volu = 0

    for s in solution:
        s_boxes = s.boxes
        vol_boxes = get_vol(s_boxes)
        acum_volu += get_vol(s_boxes)
        volumens.append(vol_boxes)

    volumens.sort()

    return volumens

""" 
    Obtiene los bins ordenados por sus volumenes de menor a mayor
    [1,2,4,11,1,23,5,123] ---(sort) --> [1, 1, 2, 4, 5, 11, 23, 123]
    tip: Agregar reverse igual True para ordenarlas de mayor a menor
"""
def get_sorted_bins(solution):

    list_solution = list(solution)
    list_solution.sort(key=lambda x: x.vol)

    return list_solution

def generate_candidate_solution(ssh,_L,_W,_H, boxes, id2box,r_param = 1.0, bsg_time=1, extra_args="--greedy_only --min_fr=0.98", verbose=False) -> list:
    global Vmax,L,W,H
    L=_L; W=_W; H=_H
    n_boxes = get_nboxes(boxes)
    
    Vmax = L*W*H
    
    solution_size = 0
    solution = []
    n_supported_items=0
    tot_support=0.0
    min_boxes_to_choose = 8

    #Generating candidate Solution
    while(len(boxes) > 0):
        solution_size +=1 
        vol_c = 0
        c = dict()

        #Llenado del contenedor
        while(vol_c < r_param*Vmax and len(boxes) != 0):
            boxes_keys = list(boxes.keys())
            r =  rd.randint(0, len(boxes_keys)-1)
            b = boxes_keys[r]
            n = min(boxes[b],min_boxes_to_choose)
            boxes[b] = boxes[b]-n

            # No quedan mas cajas del tipo b
            if(boxes[b] == 0):
                boxes.pop(b)

            # Si no se ha agregado el tipo de caja
            if(b not in c):
                c[b] = 0

            #Agregar cantidad de cajas
            c[b] = c[b]+n

            vol_box = b.vol
            vol_c = vol_c + vol_box*n

        #Evaluar contenedor cajas obtenidas 
        remaining, loaded, json_data = bsg_solve(ssh,L,W,H, c , id2box, time=bsg_time, args=extra_args, verbose=False)
        utilization = json_data["utilization"]
        support = json_data["tot_support"]
        full_supported_items = json_data["full_supported_items"]

        tot_support += support
        n_supported_items += full_supported_items
        if verbose: 
            print(utilization,end=" ")

        layout = json_data.get('layout', None)

        container = bin(solution_size, loaded, utilization, layout)
        #Se agrega la solucion
        solution.append(container)
        
        # añadiendo las restantes para ser distribuidas nuevamente
        for key in remaining:
            if(key in boxes):
                boxes[key] += remaining[key]
            else:
                boxes[key] = remaining[key]

    av_support = tot_support / n_boxes
    supported_items = n_supported_items / n_boxes
    
    if verbose: 
      print(f"Initial Solution: {len(solution)} av_support: {av_support} supported_items: {supported_items}")
    return solution

def get_vol(boxes):
    vol=0.0
    for box in boxes:
        vol += box.vol*boxes[box]
    return vol
      
def swap(solution, n=2,  max_vol_accept=1.0, tolerance=0.1, verbose=True):
    bin_A = get_random_bin(s = solution)
    bin_B = get_random_bin(s = solution, b = bin_A)
    
    iniA = bin_A.vol
    iniB = bin_B.vol
    var_ini = (iniA-1.0)**2 + (iniB.vol-1.0)**2
    
    nA = rd.randint(1, n)
    boxes_A = bin_A.pop_random_boxes(nA)
    adjvolA = get_adjusted_vol(boxes_A)
    
    nB = rd.randint(0, n)
    boxes_B = bin_B.pop_random_boxes(nB)
    adjvolB = get_adjusted_vol(boxes_B)
    
    r = tolerance*rd.random()

    condition_1 = adjvolA > adjvolB and iniB + adjvolA <= max_vol_accept + r
    condition_2 = adjvolB > adjvolA and iniA + adjvolB <= max_vol_accept + r

    if condition_1 or condition_2:
        bin_A.insert_boxes(boxes_B)
        bin_B.insert_boxes(boxes_A)
    else: 
        return -10
    
    iniA = bin_A.vol
    iniB = bin_B.vol
    var_final = (iniA-1.0)**2 + (iniB-1.0)**2
    var_diff = var_final - var_ini
    
    return var_diff


def random_swaps(best_solution, max_iter=100000, extra_args="", lb=1, max_no_improvements=50):
    if len(best_solution) == lb: return best_solution
    
    no_improvements = 0
    for i in range(max_iter):
        solution = cp.deepcopy(best_solution)
        diff_var = swap(solution, n=5,  max_vol_accept=0.65, tolerance=0.3, verbose=False) #accepting until 0.95

        if diff_var>1e-7:
            verified_solution=True

            #max_bl: maxima cantidad de bloques a generar por bsg
            #min_fr: minimo porcentaje ocupado para considerar la generación de un bloque
            verified = [b.vol for b in solution if b.verify==False]
            if not verify_solution(ssh, solution, L,W,H, id2box, bsg_time=5, args=extra_args, verbose=True):
                no_improvements +=1
                #print(no_improvements,i,"verification fails", [b.vol for b in solution if b.verify==False])
                verified_solution=False
                

            if verified_solution:
                no_improvements = 0
                print("red_var:", i, diff_var, verified)
                print("new sol:", len(solution),[b.vol for b in solution])

                best_solution = []
                for b in solution:
                    if b.vol > 1e-5: 
                        best_solution.append(cp.deepcopy(b))
             
        if no_improvements > max_no_improvements: break
        if len(best_solution) == lb: break

    return best_solution


instance_files = dataloader.load_instance()
for filename in instance_files:
    sols = []
    best_sols = []
    times = []

    tot_bins = 0
    min_bins = 1000
    start = timeit.default_timer()
    for k in range(n_runs):
        
        if instances_name == "martello":
            L,W,H,_boxes,id2box = dataloader.load_BRKGAinstance(filename=filename)
        elif instances_name == "cg":
            L,W,H,_boxes,id2box = dataloader.load_instances_elhedhli(filename=filename)
        elif instances_name == "large":
            L,W,H,_boxes,id2box = dataloader.load_LargeInstance(filename=filename)

        Vmax = L*W*H            # Volumen del contenedor

        for box in _boxes: 
            vol = box.vol/(L*W*H)
            box.vol=vol
        
        total_vol = get_vol(_boxes)
        lb = math.ceil(total_vol)


        best_solution = generate_candidate_solution(ssh, L, W, H, _boxes, id2box, r_param=r_param, bsg_time=bsg_time, extra_args=extra_args, verbose=True)
        #swaps
        if swaps=="--swaps":
            another_extra_args = f'--max_bl={max_bl} --min_fr={min_fr} --bottom_up --show_layout'
            best_solution = random_swaps(best_solution, max_iter=MAX_ITER, max_no_improvements=max_no_improvements, extra_args=another_extra_args, lb=lb)
            tot_bins += len(best_solution)
            if len(best_solution)< min_bins:
                min_bins = len(best_solution)

    stop = timeit.default_timer()
    sols.append(tot_bins/n_runs)
    best_sols.append(min_bins)
    times.append(stop - start)
    print (filename, ":", mean(sols), mean(best_sols), mean(times))