import random
import os
import json
from scp import SCPClient
from base.baseline.box import box
import pandas as pd
import re

# id l   w g  rotx roty rotz nn
# 1	 108 0 76 0	   30	1	 7


def load_BRinstance(filename, inst=1, nbox=1):
    boxes = {}
    id2box = {}
    with open(filename) as f:
        n = int(next(f))
        for i in range(n):
            next(f)
            L, W, H = [int(x) for x in next(f).split()]
            n_boxes = int(next(f))
            for it in range(n_boxes):
                id, l, rotx, w, roty, h, rotz, nn = [int(x) for x in next(f).split()]
                if i == inst - 1:
                    b = box(id, l, w, h, rotx, roty, rotz)
                    # Multiplicar nn para complejizar el problema
                    boxes[b] = nn * nbox
                    id2box[id] = b
            if i == inst - 1:
                return L, W, H, boxes, id2box








def load_productInstance(filename, nbox=1, rot_allowed=False):
    boxes = {}
    id2box = {}
    # Dataset and dimension on mm
    L, W, H = 12000, 2330, 2200
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print("La ruta {} no coincide".format(filename))
        return (
            L,
            W,
            H,
            {},
            {},
        )

    print(df)
    id = 0
    for index, row in df.iterrows():
        id += 1
        l, w, h = int(row["depth"]), int(row["width"]), int(row["height"])
        #        print("{}, {}, {}".format(l,w,h))
        if rot_allowed:
            b = box(id, l, w, h, 1, 1, 1)
        else:
            b = box(id, l, w, h, 0, 0, 0)

        boxes[b] = nbox
        id2box[id] = b

    return L, W, H, boxes, id2box



def write_instance(L, W, H, boxes, filename):
    txt = f'1\n1 0\n{L} {W} {H}\n'
    txt += str(len(boxes)) + "\n"
    for box in boxes:
        txt += f"{box.id} {box.l} {box.rotx} {box.w} {box.roty} {box.h} {box.rotz} {boxes[box]}\n"
    txt += "\n"

    text_file = open(filename, "w")
    text_file.write(txt)
    text_file.close()


def bsg_solve(
    ssh, L, W, H, boxes, id2box, time=1, args="", verbose=False, remove_instance=True
):
    filename = "tmp_instance_" + str(random.randint(10000, 99999))

    write_instance(L, W, H, boxes, filename)

    scp = SCPClient(ssh.get_transport())
    scp.put(filename, "/home/iaraya/clp/" + filename)
    if remove_instance:
        os.remove(filename)

    command = (
        "/home/iaraya/clp/BSG_CLP /home/iaraya/clp/"
        + filename
        + " -i 0 -t "
        + str(time)
        + " --json "
        + args
    )
    
    if verbose:
        print(command)

    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    json_data = json.loads(lines[-1])
    loaded = {}
    remaining = {}
    for item in json_data["loaded"]:
        loaded[id2box[item[0]]] = item[1]
    for item in json_data["remaining"]:
        remaining[id2box[item[0]]] = item[1]

    ssh.exec_command("rm /home/iaraya/clp/" + filename)

    return (
        remaining,
        loaded,
        json_data,
    )  # json_data["utilization"], json_data["tot_support"], json_data["full_supported_items"]
