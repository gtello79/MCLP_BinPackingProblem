import random
import os
import json
from scp import SCPClient
from box import box
# id l   w g  rotx roty rotz nn
# 1	 108 0 76 0	   30	1	 7

def load_BRinstance(filename, inst=1, nbox = 1):
    boxes={}; id2box={}
    with open(filename) as f:
        n = int(next(f))
        for i in range(n):
            next(f)
            L, W, H =  [int(x) for x in next(f).split()]
            n_boxes = int(next(f))
            for it in range(n_boxes):
                id, l, rotx, w, roty, h, rotz, nn = [int(x) for x in next(f).split()] 
                if i == inst-1:
                    b = box(id, l, w, h, rotx, roty, rotz)
                    # Multiplicar nn para complejizar el problema
                    boxes[b]=nn*nbox;
                    id2box[id]=b
            if i == inst-1: 
                return L,W,H,boxes,id2box
            
def load_BRKGAinstance(filename, inst=1, nbox = 1, rot_allowed=False):
    boxes={}; id2box={}
    with open(filename) as f:
        next(f)
        for i in range(inst):
            n_boxes, L, W, H =  [int(x) for x in next(f).split()]
            for it in range(n_boxes):
                l, w, h = [int(x) for x in next(f).split()] 
                if i == inst-1:
                    if rot_allowed:
                        b = box(it+1, l, w, h, 1, 1, 1)
                    else:
                        b = box(it+1, l, w, h, 0, 0, 0)
                    # Multiplicar nn para complejizar el problema
                    boxes[b]=nbox;
                    id2box[it+1]=b
            if i == inst-1: 
                return L,W,H,boxes,id2box


import re
def load_LargeInstance(filename, nbox = 1, rot_allowed=False):
    boxes={}; id2box={}
    try:
        with open(filename) as f:
            #n_boxes, L, W, H =  [int(x) for x in next(f).split()]
            L,W,H = 609,243,243 
            line = next(f)
            id=0
            while line is not None:
                values = re.findall("\d+", line)
                values = [int(v) for v in values]
                for i in range(int(len(values)/3)):
                    id +=1
                    l,w,h = values[i*3:i*3+3]
                    if rot_allowed:
                        b = box(id, l, w, h, 1, 1, 1)
                    else:
                        b = box(id, l, w, h, 0, 0, 0)  
                    boxes[b]=nbox;
                    id2box[id]=b
                line = next(f)
    except StopIteration:
        return L,W,H,boxes,id2box
           

            
        

def write_instance(L,W,H,boxes,filename) :
    txt = "1\n1 0\n"+str(L)+" "+str(W)+" "+str(H)+"\n";
    txt += str(len(boxes)) + "\n"
    for box in boxes:
        txt += str(box.id) + ' ' + str(box.l) + ' ' + str(box.rotx) \
            + ' ' + str(box.w) + ' ' + str(box.roty) \
            + ' ' + str(box.h) + ' ' + str(box.rotz) + ' ' + str(boxes[box])  + '\n'
    txt += '\n'

    text_file = open(filename, "w")
    text_file.write(txt)
    text_file.close()
    

def bsg_solve(ssh,L,W,H,boxes,id2box, time=1, args="", verbose=False):
    filename="tmp_instance_"+ str(random.randint(10000, 99999))
    
    write_instance(L,W,H,boxes,filename)
    
    scp = SCPClient(ssh.get_transport())
    scp.put(filename, "/home/iaraya/clp/"+filename)

    stdin, stdout, stderr = ssh.exec_command("/home/iaraya/clp/BSG_CLP /home/iaraya/clp/"+filename+" -i 0 -t "+str(time)+" --json " + args)
    lines = stdout.readlines()
    #print(lines[-1])
    json_data = json.loads(lines[-1])
    loaded={}; remaining={}
    for item in json_data["loaded"]:
        loaded[id2box[item[0]]]=item[1]
    for item in json_data["remaining"]:
        remaining[id2box[item[0]]]=item[1]
        
    ssh.exec_command("rm /home/iaraya/clp/"+filename)
    os.remove(filename)
    return remaining, loaded, json_data["utilization"]
