import re
from base.baseline.box import box

class DatasetLoader:
    def __init__(self, instance_name) -> None:
        self.instance_name = instance_name
        self.instances_list = self.load_instance()

    def load_instance(self):
        instance_files = []
        if self.instance_name == "martello":
            for cs in range(4, 8):
                for sz in [50, 100, 150, 200]:
                    total_instance = 10
                    for inst in range(total_instance):
                        # if cs<=5 and sz<=150 and inst <=8: continue
                        instance_files.append(
                            (f"benchs/class{cs+1}/{sz}.txt", inst + 1)
                        )

        elif self.instance_name == "cg":
            for c in range(4):
                for n_boxes in [500, 1000, 1500, 2000]:
                    for i in range(5):
                        instance_files.append(
                            f"benchs/Instance_CG/{n_boxes}/bin_pack_instance_i({i+1})_c({c+1}).txt"
                        )
        elif self.instance_name == "large":
            for n_boxes in [
                100,
                250,
                500,
                750,
                1000,
                1250,
                1500,
                1750,
                2000,
                2250,
                2500,
                2750,
                3000,
                3250,
                3500,
                3750,
                4000,
                4250,
                4500,
                4750,
                5000,
            ]:
                for i in range(15):
                    # if n_boxes==3250 and i<12: continue
                    instance_files.append(
                        f"benchs/Data_Large/L_{n_boxes}/L_{n_boxes}_{i+1}.txt"
                    )

        else:
            raise ValueError(f"Invalid instance name. {self.instance_name}")

        return instance_files

    def get_instance(self, filename):
        if self.instance_name == "martello":
            instance_name, id_instance = filename
            L, W, H, _boxes, id2box = self.load_BRKGAinstance(
                filename=instance_name, inst=id_instance
            )
        elif self.instance_name == "cg":
            L, W, H, _boxes, id2box = self.load_instances_elhedhli(
                filename=filename
            )
        elif self.instance_name == "large":
            L, W, H, _boxes, id2box = self.load_LargeInstance(filename=filename)

        return L, W, H, _boxes, id2box

    def load_BRKGAinstance(self, filename, inst=1, nbox=1, rot_allowed=False):
        boxes = {}
        id2box = {}
        with open(filename) as f:
            for i in range(inst):
                next(f)
                n_boxes, L, W, H = [int(x) for x in next(f).split()]
                VMax = L * W * H
                for it in range(n_boxes):
                    l, w, h = [int(x) for x in next(f).split()]
                    if i == inst - 1:
                        if rot_allowed:
                            b = box(it + 1, l, w, h, 1, 1, 1)
                        else:
                            b = box(it + 1, l, w, h, 0, 0, 0)
                        
                        b.vol = b.vol/VMax
                        # Multiplicar nn para complejizar el problema
                        boxes[b] = nbox
                        id2box[it + 1] = b
                # next(f)
                if i == inst - 1:
                    return L, W, H, boxes, id2box

    def load_LargeInstance(self,filename, nbox=1, rot_allowed=False):
        boxes = {}
        id2box = {}

        try:
            with open(filename) as f:
                # n_boxes, L, W, H =  [int(x) for x in next(f).split()]
                L, W, H = 609, 243, 243
                VMax = L * W * H
                line = next(f)
                id = 0
                while line is not None:
                    values = re.findall("\d+", line)
                    values = [int(v) for v in values]
                    for i in range(int(len(values) / 3)):
                        id += 1
                        l, w, h = values[i * 3 : i * 3 + 3]
                        if rot_allowed:
                            b = box(id, l, w, h, 1, 1, 1)
                        else:
                            b = box(id, l, w, h, 0, 0, 0)
                        
                        b.vol = b.vol/VMax

                        boxes[b] = nbox
                        id2box[id] = b
                    line = next(f)
        except StopIteration:
            return L, W, H, boxes, id2box

    def load_instances_elhedhli(self,filename, rot_allowed=False):
        boxes = {}
        id2box = {}
        try:
            with open(filename) as f:
                L, W, H = 1200, 800, 2055
                VMax = L * W * H
                line = next(f)
                id = 0
                while line:
                    id += 1
                    # "Width" "Depth" "Height" "Weight" "Load Capacity" "Width Reduce" "Depth Reduce" "Shape Type" "Repetition" "Sequence Number
                    w, l, h, _, _, _, _, _, nbox, _ = line.split("\t")
                    w, l, h, nbox = int(w), int(l), int(h), int(nbox)

                    if rot_allowed:
                        b = box(id, l, w, h, 1, 1, 1)
                    else:
                        b = box(id, l, w, h, 0, 0, 0)

                    b.vol = b.vol/VMax

                    boxes[b] = nbox
                    id2box[id] = b
                    line = next(f)

        except StopIteration:
            return L, W, H, boxes, id2box
