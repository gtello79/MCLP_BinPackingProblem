import random
import os
from scp import SCPClient
from box import box
import numpy as np
from bsg import bsg_solve
from bin import bin

Vmax = None; L=None; W=None; H=None

def generate_candidate_solution(ssh,_L,_W,_H, boxes, id2box,r_param = 1.0, bsg_time=1) -> list:
    global Vmax,L,W,H
    L=_L; W=_W; H=_H
    
    Vmax = L*W*H
    
    solution_size = 0
    solution = np.array([])

    #Generating candidate Solution
    while(len(boxes) > 0):
        solution_size +=1 
        vol_c = 0
        c = dict()

        #Llenado del contenedor
        while(vol_c < r_param*Vmax and len(boxes) != 0):
            boxes_keys = list(boxes.keys())
            r =  random.randint(0, len(boxes_keys)-1)
            b = boxes_keys[r]
            n = min(boxes[b],8)    
            boxes[b] = boxes[b]-n

            # No quedan mas cajas del tipo b
            if(boxes[b] == 0):
                boxes.pop(b)

            #Agregar cantidad de cajas
            if(b not in c):
                c[b] = n
            else:
                c[b] = c[b]+n
            
            vol_box = b.vol
            vol_c = vol_c + vol_box*n

        #Evaluar contenedor cajas obtenidas 
        remaining, loaded, utilization = bsg_solve(ssh,L,W,H, c , id2box, time=bsg_time)
        container = bin(solution_size, loaded, utilization)
        #Se agrega la solucion
        solution = np.append(solution, container)
        
        # añadiendo las restantes para ser distribuidas nuevamente
        for key in remaining:
            if(key in boxes):
                boxes[key] += remaining[key]
            else:
                boxes[key] = remaining[key]

    print("Initial Solution: {}".format(len(solution)))
    return solution

def print_solution(solution:list):
    sol_size = 0
    for s in solution:
        
        vol = get_vol_by_boxes_group(boxes = s.boxes)
        if vol != 0.0 :
            print("id: {} - vol: {}".format(s.id, vol))
            sol_size+=1
        
    print("Solution Size: {}".format(sol_size))
    
# Retorna la probabilidad de llenar el
def calculate_prob(solution: list, metric:float) -> float:
    counter = 0
    size = 0
    for s in solution:
        if(len(s.boxes) != 0):
            size+=1
            v = get_vol_by_boxes_group(s.boxes)
            if(v > metric):
                counter += 1


    prob_calculate = (float)(counter/size)
    return prob_calculate

def get_media_volumen(solution:list) -> float:
    ponderate = 0
    size = 0

    for s in solution:
        bin_boxes = s.boxes
        if(len(bin_boxes) != 0):
            ponderate += get_vol_by_boxes_group(bin_boxes)
            size+=1 
    
    media = float(ponderate/size)
    return media    

import random
def get_random_bin(s:list, b:bin = None) -> object:
    
    get_id = int(random.randint(0, len(s)-1))
    bin_selected = s[get_id]

    #Se retorna un bin distinto al seleccionado y que no este vacio
    while(b == bin_selected or len(bin_selected.boxes) == 0):
        get_id = int(random.randint(0, len(s)-1))
        bin_selected = s[get_id]
    
    return bin_selected

def pop_random_boxes_from_bin(last_bin: object, cant_boxes: int) -> dict:
    boxes_to_share = dict()
    boxes = last_bin.boxes

    for i in range(cant_boxes):
        total_keys = list(boxes.keys())
        
        #Selecciona una caja aleatoria
        get_id = int(random.randint(0, len(total_keys)-1))
        box = total_keys[get_id]
        boxes[box] = boxes[box]-1

        # Agrega la caja al conjunto
        if(box not in boxes_to_share):
            boxes_to_share[box] = 1
        else:
            boxes_to_share[box] = boxes_to_share[box]+1
        
        # Elimina la caja del conjunto si no quedan mas
        if(boxes[box] == 0):
            boxes.pop(box)
        
        if(len(boxes) == 0):
            break
    
    return boxes_to_share

def eval_list_bins(solution:list, media) -> float:
    quality = 0.0

    for b in solution:
        bin_boxes = b.boxes
        diff = get_vol_by_boxes_group(bin_boxes) - media
        quality += pow(diff,2)

    return quality

def verify_solution(ssh, solution: list, id2box, bsg_time=5) -> bool:
    factibility = True
    for s in solution:
        if(not(s.verify)):
            boxes = s.boxes
            persistens = True
            while(persistens):
                try:
                    remaining, loaded, s.utilization = bsg_solve(ssh,L,W,H, boxes, id2box, time=bsg_time)
                    persistens = False
                except:
                    persistens = True

            if(len(remaining) != 0):
                return False
            else: s.verify = True
                
    return factibility

def random_swap(solution:list, media_volumen:float, verbose=False):
    # Seleccionar bin 1 y 2 
    bin_1 = get_random_bin(s = solution) 
    bin_2 = get_random_bin(s = solution, b = bin_1)
    
    v1 = get_vol_by_boxes_group(bin_1.boxes)
    v2 = get_vol_by_boxes_group(bin_2.boxes)

    var_initial = eval_list_bins([bin_1, bin_2], media_volumen)

    if verbose:
        print("Initial ")
        print("Bin 1: {} ".format(v1))
        print("Bin 2: {} ".format(v2))
        print("Var:", var_initial)

    # Seleccionar boxes del bin 1
    total_boxes = int(random.randint(1, 2))
    boxes_1 = pop_random_boxes_from_bin(last_bin=bin_1, cant_boxes=total_boxes)

    # Se agregan cajas de bin_1 en bin_2
    for box in boxes_1:
        if(box not in bin_2.boxes):
            bin_2.boxes[box] = boxes_1[box]
        else:
            bin_2.boxes[box] = bin_2.boxes[box] + boxes_1[box]
    bin_2.verify = False
    
    v2 = get_vol_by_boxes_group(bin_2.boxes)
    
    # Probabilidad de poder llenar el bin 2
    # Probabilidad = Proporcion de bins con volumen mayor a v2

    p1 = None
    p2 = calculate_prob(solution, v2)
    # Seleccionar cajas desde el bin b_2
    while( p2 <= random.random() ):
            
        v1 = get_vol_by_boxes_group(bin_1.boxes)
        v2 = get_vol_by_boxes_group(bin_2.boxes)
        p1 = calculate_prob(solution, v1)
        
        # Se espera solo una caja desde bin_2
        boxes_2 = pop_random_boxes_from_bin(last_bin=bin_2, cant_boxes= 1)
        box_2 = list(boxes_2.keys())[0] 

        if(predict_vol(bin_1.boxes, box_2) > 1 ):
            # print("La caja escogida sobrepasa el máximo del bin 1")
            return None, -1  

        # Se agrega la caja al conjunto del bin2 
        if(box_2 not in bin_1.boxes):  
            bin_1.boxes[box_2] = 1
        else:
            bin_1.boxes[box_2] = bin_1.boxes[box_2] + 1
        bin_1.verify = False

        v1 = get_vol_by_boxes_group(bin_1.boxes)
        v2 = get_vol_by_boxes_group(bin_2.boxes)
        p2 = calculate_prob(solution, v2)
        p1 = calculate_prob(solution, v1) # -> 0: No se puede llenar

        if( p1 <= random.random()):
            return None, -1

        if(len(bin_2.boxes) == 0):
            # print("Empty bin 2")
            break
    
    if(v2 > 1):
        # print("Sobrepasa Volumen del bin 2")
        return None, -1
    else:
        if verbose: print("After Swap")
        v1 = get_vol_by_boxes_group(bin_1.boxes)
        v2 = get_vol_by_boxes_group(bin_2.boxes)  
        bin_1.utilization = v1
        bin_2.utilization = v2
        bin_1.p = p1
        bin_2.p = p2
        
        var_final = eval_list_bins([bin_1, bin_2], media_volumen)
        eval = var_final - var_initial
        
        if verbose:
            print("Bin 1: {} ".format(v1))
            print("Bin 2: {} ".format(v2))
            print("prob:", p1, p2)
            print("Varianza Inicial: {}. Varianza final: {}".format(var_initial, var_final ))

        return solution, eval


# El bin debería mantener su volumen actualizado y
# estas funciones no deberían utilizarse
def get_vol_by_boxes_group(boxes: dict) -> float:
    vol = 0.0
    for box in boxes:
        vol += box.vol*boxes[box]
    final_vol = float(vol/Vmax)
    
    return final_vol

def predict_vol(boxes:dict, box: object) -> float:
    vol_box = box.vol
    vol_bin = get_vol_by_boxes_group(boxes)
    total_vol = float(vol_box/Vmax) + vol_bin
    return total_vol