import random

class bin:
    def __init__(self, id, boxes, utilization, layout=None):
        self.id:int = id
        self.boxes: dict = boxes
        self.utilization:float = utilization
        self.verify:bool = True
        self.vol:float = 0.0
        self.layout = layout

        self.calculate_boxes()
        self.calculate_vol()


    def insert_boxes(self, boxes):
        for box in boxes:

            if box not in self.boxes:
                self.boxes[box] = 0

            self.boxes[box] += boxes[box]

            self.vol += box.vol*boxes[box]

        self.verify = False   

    def pop_random_boxes(self, n):
        boxes_to_share = dict()
        boxes = self.boxes

        for i in range(n):
            total_keys = list(boxes.keys())

            #Selecciona una caja aleatoria
            get_id = random.randint(0, len(total_keys)-1)
            box = total_keys[get_id]
            boxes[box] = boxes[box]-1
            self.vol -= box.vol

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

    def calculate_boxes(self) -> int:
        n = 0
        for box in self.boxes:
            n += self.boxes[box]
        return n

    def calculate_vol(self) -> float:
        self.vol=0.0

        for box in self.boxes:
            self.vol += box.vol*self.boxes[box]

        return self.vol

    @classmethod
    def get_nboxes(cls, boxes):
        n = 0
        for box in boxes:
            n += boxes[box]
        return n 

    @classmethod
    # El bin debería mantener su volumen actualizado y
    # estas funciones no deberían utilizarse
    def get_vol_by_boxes_group(cls, boxes: dict) -> float:
        final_vol = 0.0
        for box in boxes:
            final_vol += box.vol * boxes[box]

        return final_vol
