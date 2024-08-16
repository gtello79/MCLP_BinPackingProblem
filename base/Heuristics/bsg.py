import random
import os
import json
from json.decoder import JSONDecodeError
from scp import SCPClient

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
    loaded = {}
    remaining = {}

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
    try:
        json_data = json.loads(lines[-1])
    except (JSONDecodeError, IndexError) as e:
        import pdb; pdb.set_trace()
        raise(e)

    for item in json_data["loaded"]:
        loaded[id2box[item[0]]] = item[1]
    for item in json_data["remaining"]:
        remaining[id2box[item[0]]] = item[1]

    ssh.exec_command("rm /home/iaraya/clp/" + filename)

    return (
        remaining,
        loaded,
        json_data,
    )
