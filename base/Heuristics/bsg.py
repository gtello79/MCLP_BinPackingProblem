import random
import os
import subprocess
import json
from json.decoder import JSONDecodeError
from scp import SCPClient
from base.INSTACE_PARAM import LOCAL_EXECUTION

# id l   w g  rotx roty rotz nn
# 1	 108 0 76 0	   30	1	 7


def write_instance(L, W, H, boxes, filename):
    txt = f"1\n1 0\n{L} {W} {H}\n"
    txt += str(len(boxes)) + "\n"
    for it_box in boxes:
        txt += f"{it_box.id} {it_box.l} {it_box.rotx} {it_box.w} {it_box.roty} {it_box.h} {it_box.rotz} {boxes[it_box]}\n"
    txt += "\n"

    text_file = open(filename, "w")
    text_file.write(txt)
    text_file.close()


def bsg_solve(
    ssh, L, W, H, boxes, id2box, time=1, args="", verbose=False, remove_instance=True
):

    index_results = -1
    BSG_PATH = "/home/iaraya/clp"
    filename = "tmp_instance_" + str(random.randint(10000, 99999))
    write_instance(L, W, H, boxes, filename)

    loaded = {}
    remaining = {}

    # Permite una ejecución local del BSG_CLP
    if LOCAL_EXECUTION:
        BSG_PATH = "."
        index_results = -2

        command = [f'{BSG_PATH}/BSG_CLP',f'{BSG_PATH}/{filename}', '-i', '0', '-t', f'{time}', '--json']
        
        args = args.split(" ")

        if args.__len__() > 0:
            command.extend(args)

        if verbose:
            print(command)

        lines = subprocess.run(command, capture_output=True, text=True).stdout.split('\n')

    else:
        # Permite una ejecución por vía SSH en un servidor remoto
        scp = SCPClient(ssh.get_transport())
        scp.put(filename, f"{BSG_PATH}/" + filename)

        command = f"{BSG_PATH}/BSG_CLP {BSG_PATH}/{filename} -i 0 -t {time} --json {args}"

        if verbose:
            print(command)

        stdin, stdout, stderr = ssh.exec_command(command)
        lines = stdout.readlines()

        # Elimina archivo creado en el servidor
        ssh.exec_command(f"rm {BSG_PATH}" + filename)
    

    # Se obtiene el resultado de la ejecución
    try:
        json_data = json.loads(lines[index_results])
    except (JSONDecodeError, IndexError) as e:
        import pdb
        pdb.set_trace()
        raise (e)

    for item in json_data["loaded"]:
        loaded[id2box[item[0]]] = item[1]
    for item in json_data["remaining"]:
        remaining[id2box[item[0]]] = item[1]

    if remove_instance:
        os.remove(filename)

    return (
        remaining,
        loaded,
        json_data,
    )
