from numpy.lib.function_base import _calculate_shapes
import random


class bin:
    def __init__(self, id, boxes, utilization):
        self.id = id
        self.boxes = boxes
        self.utilization = utilization
        self.verify = True
        
    def set_adj_vol(self, adj_vol):
        self.adj_vol = adj_vol
        
    def insert_boxes(self, boxes):
        for box in boxes:
            if box not in self.boxes:
                self.boxes[box] = boxes[box]
            else:
                self.boxes[box] = self.boxes[box] + boxes[box]
            self.adj_vol += box.adj_vol*boxes[box]
        self.verify = False   
        
    
    def pop_random_boxes(self, n):
        boxes_to_share = dict()
        boxes = self.boxes

        for i in range(n):
            total_keys = list(boxes.keys())

            #Selecciona una caja aleatoria
            get_id = int(random.randint(0, len(total_keys)-1))
            box = total_keys[get_id]
            boxes[box] = boxes[box]-1
            self.adj_vol -= box.adj_vol

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


    def getMostComplex(self):
        idBox = None
        eval = 0
        for b in self.boxes:
            if(idBox is None):
                idBox = b.idBox
            else:
                if(b.complex > eval):
                    idBox = b.idBox
                    eval = b.complex
        return idBox, eval    

    def getBox(self, idBox):
        for b in self.boxes:
            if (idBox == b.idBox):
                return b 
            else:
                continue   

    def getAllIndex(self):
        idBoxes = [ b.idBox for b in self.boxes ]
        return idBoxes

    def __str__ (self) -> str:
        boxes_list = ''
        for box in self.boxes.keys():
            boxes_list = boxes_list + str([box.id, self.boxes[box]]) + ", "
        return boxes_list